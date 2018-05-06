from django import forms

from PIL import Image, ImageOps

from .models import InputImage


class InputImageForm(forms.ModelForm):
    class Meta:
        model = InputImage
        fields = ('description', 'copyright_notice', 'image')

    def save(self):
        image = super(InputImageForm, self).save()

        original_image = Image.open(image.image)

        min_dimension = min(original_image.size)

        output_size = (1000, 1000) if min_dimension > 1000 else (
            min_dimension, min_dimension)

        fixed_image = ImageOps.fit(original_image, output_size)

        fixed_image.save(image.image.url)

        return image
