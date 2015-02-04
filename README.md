# musiClr
Automated music tagging application for easily cleaning a music library.

## Example usage
* Run the application
* Select a directory which contains all your music
* Click 'Run script'

The application will try to parse through the file names of each .mp3 file and extract the artist and title tags. After it is finished the program will display a summary showing which .mp3s were parsed successfuly. On this screen you will be given the option to tweak the resulting tags or add tags to any mp3s which were skipped.

## Dependencies
* [python-taglib](https://code.google.com/p/python-taglib/) 
* [wxPython](http://www.wxpython.org/)
* [py2exe](http://www.py2exe.org/) (if you want to create a standalone executable)


