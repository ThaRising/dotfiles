# Dotfiles

A collection of my dotfiles.

An installation file is included, which
by default, will overwrite existing files.  

You can change this behaviour by changing
the parameter 'force' of the function
'recursive_copymerge', to False.  

You can run the installation file, like so:
```bash
python3 install.py
```

### dconf.dump

Import the dconf.dump file like so:
```bash
dconf load /org/gnome/settings-daemon/ < ~/dconf/org.gnome.settings-daemon
# Do the same for the other files
```
