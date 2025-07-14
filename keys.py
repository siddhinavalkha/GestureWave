import cv2

class Key:
    def __init__(self, x, y, w, h, text):
        """
        Initialize a virtual key.
        
        Parameters:
        - x, y: Top-left corner of the key.
        - w, h: Width and height of the key.
        - text: Text displayed on the key.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def drawKey(self, img, bgColor=(200, 200, 200), textColor=(0, 0, 0), alpha=0.5):
        """
        Draw the key on the given image.

        Parameters:
        - img: The image on which to draw the key.
        - bgColor: Background color of the key (BGR format).
        - textColor: Color of the text on the key (BGR format).
        - alpha: Opacity of the background (0.0 to 1.0).
        """
        if img is None or not img.size:
            print("Error: Invalid image for drawing.")
            return

        # Validate dimensions
        if self.w <= 0 or self.h <= 0:
            print("Error: Invalid key dimensions.")
            return

        # Draw the semi-transparent background
        overlay = img.copy()
        cv2.rectangle(overlay, (self.x, self.y), (self.x + self.w, self.y + self.h), bgColor, cv2.FILLED)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # Calculate text size and position to center it
        textSize = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        textX = self.x + (self.w - textSize[0]) // 2  # Center text horizontally
        textY = self.y + (self.h + textSize[1]) // 2  # Center text vertically

        # Draw the text
        cv2.putText(img, self.text, (textX, textY), cv2.FONT_HERSHEY_SIMPLEX, 1, textColor, 2)

    def isOver(self, x, y):
        """
        Check if a given point (x, y) is over the key.

        Parameters:
        - x, y: Coordinates of the point.

        Returns:
        - True if the point is within the key's bounds, False otherwise.
        """
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
