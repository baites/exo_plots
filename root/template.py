#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 14, 2012
Copyright 2011, All rights reserved
'''

from __future__ import print_function

import os
import sys

import root.tfile

import ROOT

class Template(object):
    '''
    ROOT Histogram wrapper with additional information saved:

        filename    file where temlate was loaded from
        path        path inside the file where histogram was found
        name        template name
        dimension   histogram dimension
        hist        plot object

    All attributes are automatically extracted from plot. Filename and
    path are obtained using TH1::GetDirectory() if available.
    
    The template is invalidated if invalid (None) histogram is assigned.

    Only 1D, 2D and 3D plots are supported.
    '''

    def __init__(self, hist = None, clone = False, template = None):
        '''
        Initialize template with optional histogram and define if any
        histogram assignments should clone plot
        '''

        self.__clone = clone

        if template:
            self.__filename = template.filename
            self.__path = template.path

            self.hist = template.hist
        else:
            self.__filename = ""
            self.__path = ""

            self.hist = hist

    @property
    def filename(self):
        '''
        Filename where template was loaded from including folders

            input_file.root
        '''

        return self.__filename

    @property
    def path(self):
        '''
        Path to template in file, e.g.:

            /path/to/template
        '''

        return self.__path

    @property
    def name(self):
        '''
        Template name
        '''

        return self.__name

    @property
    def dimension(self):
        '''
        Template dimension
        '''

        return self.__dimension

    @property
    def hist(self):
        '''
        Template histogram object
        '''

        return self.__hist

    @hist.setter
    def hist(self, obj):
        '''
        Set hist object only in case it has a supported Dimension value.
        Othewise, set hist to None
        '''

        if obj:
            # Make sure template has supported dimension
            dim = obj.GetDimension()
            if dim not in [1, 2, 3]:
                raise ValueError("unsupported template dimension: " + str(dim))

            directory = obj.GetDirectory()
            if directory:
                directory = directory.GetPath().rstrip("/")
                self.__filename, self.__path = directory.rsplit(':', 1)

            self.__dimension = dim
            self.__name = obj.GetName()

            if self.__clone:
                obj = obj.Clone()
                obj.SetDirectory(0)

            self.__hist = obj
        else:
            # Invalidate template
            self.__filename = ""
            self.__path = ""
            self.__name = ""
            self.__dimension = None
            self.__hist = None

    @hist.deleter
    def hist(self):
        '''
        Remove hist property
        '''

        del self.__hist

    def __nonzero__(self):
        '''
        Python 2.x hook
        '''

        return self.__bool__()

    def __bool__(self):
        '''
        Template is assumed to be valid only in case its dimension
        and histogram are set
        '''

        return bool(self.hist)

    def __str__(self):
        '''
        Nice-print of the template
        '''

        if self:
            format_string = ("<{Class} {name!r} {dim}D in "
                             "'{filename}:{path}' at 0x{ID:x}>")
        else:
            format_string = "<{Class} invalid template at 0x{ID:x}>"

        return format_string.format(
                    Class = self.__class__.__name__,
                    dim = self.dimension,
                    name = self.name,
                    filename = self.filename,
                    path = self.path,
                    ID = id(self))


class TemplateLoader(object):
    '''Load template histograms from ROOT file

    Templates may be kept in TDirectories.
    '''

    # List of folders to be skipped in loading
    use_folders = []
    ban_folders = []

    # list plots to be loaded
    use_plots = []
    ban_plots = []

    def __init__(self):
        '''The class keeps track of loaded plots only'''

        self.templates = []

    def load(self, filename):
        '''Loading entry point'''

        if not os.path.exists(filename):
            raise RuntimeError(("templates file does not exist "
                                "{0!r}").format(filename))

        # clean-up any previously loaded templates
        if self.templates:
            self.templates = []

        with root.tfile.topen(filename) as input_:
            # Scan file recursively for plots
            self.load_plots(directory=input_, path="")

    def process_plot(self, template):
        '''
        Callback for every template loaded

        Custom classes should override this function to process templates
        as these are loaded if needed
        '''

        self.templates.append(template)

    def process_folder(self, folder, path):
        '''
        Callback for subfolders
        '''

        self.load_plots(folder, path)

    def load_plots(self, directory, path):
        '''
        Find path in directory and scan it for histogrmas and subfolder.
        '''

        # make sure path can be found in the directory
        folder = directory.GetDirectory(path)
        if not folder:
            raise RuntimeError(("sub-dir {0!r} is not found "
                                "in {1!r}").format(path, directory.GetPath()))

        # scan through all available objects in current folder
        for key in (x.GetName() for x in folder.GetListOfKeys()):
            obj = folder.Get(key)
            if not obj:
                raise RuntimeError(("failed to extract object {0!r} "
                                    "in {1!r}").format(key, folder.GetPath()))

            if isinstance(obj, ROOT.TH1):
                plot = Template(clone = True)
                plot.hist = obj

                self.process_plot(plot)

            elif isinstance(obj, ROOT.TDirectory):
                self.process_folder(folder, key)



if "__main__" == __name__:
    import unittest

    class TestTemplate(unittest.TestCase):
        def test_template_path(self):
            template = Template()
            self.assertEqual(template.path, "")

        def test_template_name(self):
            template = Template()
            self.assertEqual(template.name, "")

        def test_template_dimension(self):
            template = Template()
            self.assertEqual(template.dimension, None)

        def test_template_hist(self):
            template = Template()
            self.assertEqual(template.hist, None)

        def test_template_hist_no_clone(self):
            template = Template()
            hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)
            template.hist = hist

            self.assertEqual(template.hist, hist)

        def test_template_hist_clone(self):
            template = Template(clone = True)
            hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)
            template.hist = hist

            self.assertNotEqual(template.hist, hist)

        def test_hist_1d_path(self):
            template = Template()
            template.hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)

            self.assertEqual(template.path, "")

        def test_hist_1d_name(self):
            template = Template()
            template.hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)

            self.assertEqual(template.name, "hist_1d")

        def test_hist_1d_dim(self):
            template = Template()
            template.hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)

            self.assertEqual(template.dimension, 1)

        def test_hist_1d_hist(self):
            template = Template()
            hist = ROOT.TH1F("hist_1d", "hist_1d", 10, 0, 10)
            template.hist = hist

            self.assertEqual(template.hist, hist)

        def test_hist_2d_path(self):
            template = Template()
            template.hist = ROOT.TH2F("hist_2d", "hist_2d",
                                      10, 0, 10, 10, 0, 10)

            self.assertEqual(template.path, "")

        def test_hist_2d_name(self):
            template = Template()
            template.hist = ROOT.TH2F("hist_2d", "hist_2d",
                                      10, 0, 10, 10, 0, 10)

            self.assertEqual(template.name, "hist_2d")

        def test_hist_2d_dim(self):
            template = Template()
            template.hist = ROOT.TH2F("hist_2d", "hist_2d",
                                      10, 0, 10, 10, 0, 10)

            self.assertEqual(template.dimension, 2)

        def test_hist_2d_hist(self):
            template = Template()
            hist = ROOT.TH2F("hist_2d", "hist_2d",
                             10, 0, 10, 10, 0, 10)
            template.hist = hist

            self.assertEqual(template.hist, hist)

        def test_hist_3d_path(self):
            template = Template()
            template.hist = ROOT.TH3F("hist_3d", "hist_3d",
                                      10, 0, 10, 10, 0, 10, 10, 0, 10)

            self.assertEqual(template.path, "")

        def test_hist_3d_name(self):
            template = Template()
            template.hist = ROOT.TH3F("hist_3d", "hist_3d",
                                      10, 0, 10, 10, 0, 10, 10, 0, 10)

            self.assertEqual(template.name, "hist_3d")

        def test_hist_3d_dim(self):
            template = Template()
            template.hist = ROOT.TH3F("hist_3d", "hist_3d",
                                      10, 0, 10, 10, 0, 10, 10, 0, 10)

            self.assertEqual(template.dimension, 3)

        def test_hist_3d_hist(self):
            template = Template()
            hist = ROOT.TH3F("hist_3d", "hist_3d",
                             10, 0, 10, 10, 0, 10, 10, 0, 10)
            template.hist = hist

            self.assertEqual(template.hist, hist)

    unittest.main()
