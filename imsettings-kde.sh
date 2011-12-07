# workaround for KDE
if [ -f /etc/X11/xinit/xinitrc.d/50-xinput.sh ] ; then
   DISABLE_IMSETTINGS=1 DRY_RUN=1 . /etc/X11/xinit/xinitrc.d/50-xinput.sh
fi
