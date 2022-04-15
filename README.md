# rofi-set-audio

Rofi scripts to set audio sinks, sources and profiles.

# Install

```
cp rofi-set-audio.py ~/.local/bin/
```

# Usage

A simple example showing how to launch the audio menu:

```
rofi -show audio-menu -modi "audio-menu:rofi-set-audio.py"
```

If you didn't install the script in PATH, you need to give the path to the script. If you're running rofi under this directory where the script is, you can run it as follows:

```
rofi -show audio-menu -modi "audio-menu:./rofi-set-audio.py"
```

# Dependencies

* `python3.9` or newer;
* `requirements.txt` for runtime dependencies;
* `requirements_dev.txt` for development dependencies.
