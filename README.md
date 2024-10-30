# pocket.widget
 
Simple widget to showcase your latest saved articles on [Pocket](https://getpocket.com).

## Usage
Simply run `pocket-api.py 1234-abcd1234abcd1234abcd1234` with your [consumer key](https://getpocket.com/developer/docs/authentication) to generate the `widget.html` in the `src\web` folder.

The script will attempt to save any keys, codes, and tokens as the following files:
- `src\ACCESS_CODE`
- `src\ACCESS_TOKEN`
- `src\CONSUMER_KEY`

These will be used for subsequent runs.

### Options
- Compact size: You can toggle compact size by setting the `compact` class on the body tag. Compact mode is about 42% smaller.
- Dark mode: You can toggle dark mode by specifying `?theme=dark` after the generated html page address.

## Screenshots

### Full Size
![preview.png](preview.png)
![preview.dark.png](preview.dark.png)

### Compact Size
![preview.compact.png](preview.compact.png)
![preview.dark.compact.png](preview.dark.compact.png)