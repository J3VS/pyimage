## pyimage

experimental utils/query builder for finding text in images

### Example

```py
from pyimage.screenshot import AbstractScreenShotSearch
from pyimage.read import PreProcess

class ImageScraper(AbstractScreenShotSearch): 
    def __init__(self, image_path):
        super().__init__(image_path, preprocesses=[PreProcess.GRAY, PreProcess.ADAPTIVE_THRESH])

    def get_amount(self):
        return self.find_value_to_right("Amount")

def read_amount(image_path):
    return ImageScraper(image_path).get_amount()
```