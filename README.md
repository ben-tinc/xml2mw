# xml2mw
Parse confluence xml export and generate pages with mediawiki markup. 

## Usage
 
 * Clone this repo and `cd xml2mw`.
 * Use `pipenv install` to install all dependencies (or ensure for yourself that you use `python3` and that `lxml` and `anytree` are installed). If using `pipenv`, type `pipenv shell` afterwards to enter the virtualenv.
 * Place the `entities.xml` file from the confluence export inside a `data` subdirectory (or adjust the `XML_PATH` setting in the script).
 * Optionally adjust `OUT_PATH`, which specifies where result text files will be placed.
 * Run `python xml2mw.py`.

Now, result files should be in `OUT_PATH`, and a file `sitemap.txt` should be in the base directory.

## Test suite

If you want to run the test suite, just run `python -m unittest discover`. Using `pytest` should work as well, if you prefer that. `pytest` is included in the development dependencies, which you can install with `pipenv install --dev`.
