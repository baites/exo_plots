## root.template

This is the base class for all the template(s) loading. The module contains
two classes:

* **Template** is a wrapper around ROOT.TH1 that stores a bunch of inromation
about the plot:
    * _filename_ from which the template was loaded
    * _path_ inside the file where histogram was found
    * _name_ of the plot object
    * _dimension_ of the histogram
    * _hist_ plot object
* **TemplateLoader** a Template(s) loader from ROOT file

## How it works

The TemplateLoader class entry method is
```TemplateLoader::load("filename.root")```. It will open file and go over all
the keys.

The template is loaded if corresponding object is a histogram. In case of
TDirectory the loader will jump into that folder and load all the histograms
from that folder.

The code will go all the way deep into directory tree to load all found plots.

TemplateLoader has two outlet functions:
```TemplateLoader::process_plot(template)``` and
```TemplateLoader::process_folder(folder, path)```. This can be overriden in
the child classes to define policy on what plots to store or what folders to
skip

## Example

Let's review a very simple example of custom template loader that skips all the
folders and only loads plots that start with _mass_ word.

```python
class MassLoader(TemplateLoader):
    def __init__(self):
        TemplateLoader.__init__(self)

    def process_folder(self, folder, path):
        '''Skip all folders'''

        pass

    def process_plot(self, template):
        '''Store only templates whose name's start with mass'''

        if template.name.startswith("mass"):
            TemplateLoader.process_plot(template)
```
