![PyPI](https://img.shields.io/pypi/v/easycontrol) ![PyPI - Downloads](https://img.shields.io/pypi/dw/easycontrol) ![PyPI - License](https://img.shields.io/pypi/l/easycontrol)
# EasyControl
An easy-to-use template for creating a fully working userbot on Telegram.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install EasyControl.
```bash
pip install easycontrol
```

## Usage
Create a file, usually I name it ```main.py```, put the following code in it and replace the samples of api-id and the api-hash with your real ones.
```python
from easycontrol import EasyControl

def main():
    EasyControl(1234567, '1234567890abcdefghilmABCDEFGHILM')
    
if __name__ == '__main__':
    main()
```
Now create a directory named ```modules``` in the same directory where the ```main.py``` file is located and put in it all the modules that you want your userbot to have.

After that just execute the ```main.py``` file and start using your userbot!

If you want to change the modules directory, after executing the ```main.py``` file once a ```config.json``` file will be created in its same directory. Just change the ```modules_path``` param with the new path of the modules directory.

## Support
If you need some help you can contact me on Telegram at [@lesbicazzo](https://t.me/lesbicazzo).

## License
[MIT](https://choosealicense.com/licenses/mit/)