# Instructions 

To install the code one needs to use the application configuration file.
It is used to reduce number of options passed to the script in command line.

The config is kept in the **~/.exo/template.yaml*** file. User has several
options to run the code:

1. manualy create a folder, copy the template
[configuration file](https://github.com/ksamdev/exo_plots/blob/master/config/config.yaml),
and set paths to channels and plots configuration files
2. run **install.py** script to do everything automatically
3. supply configuration via script option
```bash
./template_main.py --config my_config.yaml
```

After this the system is ready for run. Make sure the **setup.sh** script is
run in the new shell session, e.g.:

```bash
source ./setup.sh
```
