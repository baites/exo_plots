# Dependencies

* [Python](http://www.python.org) 2.6+
* [ROOT](http://root.cern.ch) 5.28+
* [PyYAML](http://pyyaml.org/wiki/PyYAML) 3.0+

# PyYAML

YAML is a human readable and easy to support configuration language that is
intensively used by many large companies. The installations instructions
are layed out below for two scenarios: with and without ```sudo``` priviledges.

## With SUDO

The PyYAML can be easily installed with Python package manager
```easy_install``` on the node with admin priviledges:

```bash
sudo easy_install pyyaml
```

Note: it may not work on the Mountain Lion due to a bug in the Pythons
setuptools. Then use instead:

```bash
sudo python -m easy_install pyyaml
```

## No SUDO

Follow the instructions below to build YAML library:

```bash
# download the source
mkdir ~/downloads
cd ~/downloads
wget http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz
tar -xzf PyYAML-3.10.tar.gz
cd PyYAML-3.10
# compile the code
python ./setup.py --without-libyaml build
# let Python know where lib is
cat << eof >> ~/.bash_profile
export PYTHONPATH=$PWD/build/lib.linux-x86_64-2.4:\$PYTHONPATH
eof
```

You are setup and good to go.

# Instructions 

The code needs to install a configuration fie into
```$HOME/.exo/template.yaml``` before it can be used. Run an installation
script:

```bash
./install.py
```

After this step the system is ready for use. Make sure you run the
```setup.sh``` to setup the environment before any script is executed:

```bash
source ./setup.sh
```
