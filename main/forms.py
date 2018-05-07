from django import forms

from PIL import Image, ImageOps

from .models import InputImage, Job


OUTPUT_IMAGE_SIZE = 600


class InputImageForm(forms.ModelForm):
    class Meta:
        model = InputImage
        fields = ('description', 'copyright_notice', 'image', 'visibility')

    def save(self):
        image = super(InputImageForm, self).save()

        original_image = Image.open(image.image)
        min_dimension = min(original_image.size)

        output_size = (OUTPUT_IMAGE_SIZE, OUTPUT_IMAGE_SIZE) if min_dimension > OUTPUT_IMAGE_SIZE else (
            min_dimension, min_dimension)

        fixed_image = ImageOps.fit(original_image, output_size)
        # overwrite original image
        fixed_image.save(image.image.url)
        return image


class ChooseParamtersForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('visibility', 'style_weight', 'content_weight', 'num_steps')


class UpdateVisiblityJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('visibility',)


class UpdateInputImageForm(forms.ModelForm):
    class Meta:
        model = InputImage
        fields = ('visibility', 'description', 'copyright_notice')
