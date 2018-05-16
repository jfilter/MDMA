from io import BytesIO

from django import forms
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.forms import NumberInput
from PIL import Image, ImageOps

from .models import InputImage, Job

OUTPUT_IMAGE_SIZE = 600


class InputImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InputImageForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = 'Title (optional)'
        self.fields['description'].label = 'Description (optional)'
        self.fields['copyright_notice'].label = 'Copyright notice (if it\'s not your image)'
        self.fields[
            'public_domain'].label = 'This image is my own work. I hereby waive all copyright and related or neighboring rights together with all associated claims and causes of action with respect to this work to the extent possible under the law ("CC0")'

    class Meta:
        model = InputImage
        fields = ('image', 'title', 'description', 'public_domain',
                  'copyright_notice', 'visibility')

    def clean(self):
        cleaned_data = super().clean()
        pubic_domain = cleaned_data.get("public_domain")
        copyright_notice = cleaned_data.get("copyright_notice")

        if not pubic_domain and (copyright_notice is None or copyright_notice == ''):
            raise forms.ValidationError(
                "If this is not your image or you don't want to release it into public domain, please write a copy right notice. If you upload works that are in the public domain (\"CC0\"), just make a short remark in the copyright notice field. Thanks!"
            )

    def save(self):
        input_image_form = super(InputImageForm, self).save()

        original_image = Image.open(input_image_form.image)
        min_dimension = min(original_image.size)

        output_size = (OUTPUT_IMAGE_SIZE, OUTPUT_IMAGE_SIZE) if min_dimension > OUTPUT_IMAGE_SIZE else (
            min_dimension, min_dimension)

        fixed_image = ImageOps.fit(original_image, output_size)

        # why do I have to get the URL like this?
        fixed_image_path = f"input/{input_image_form.image.url.split('/')[-1]}"

        # convert transparency to white so we cane save them as JPGEG
        if fixed_image.mode in ('RGBA', 'LA'):
            background = Image.new(
                fixed_image.mode[:-1], fixed_image.size, '#ffffff')
            background.paste(fixed_image, fixed_image.split()[-1])
            fixed_image = background
            default_storage.delete(fixed_image_path)  # delete PNG file
            fixed_image_path = f"{fixed_image_path.split('.')[0]}.jpg"

        # overwrite original image
        # because it's hosted via S3, it's a little bit more complicated
        fixed_image_file_string = BytesIO()
        fixed_image.save(fixed_image_file_string, 'JPEG')

        default_storage.save(fixed_image_path, ContentFile(
            fixed_image_file_string.getvalue()))

        return input_image_form


class ChooseParamtersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['style_weight'].widget = NumberInput(
            attrs={'type': 'range', 'min': '0', 'max': '1', 'step': 'any', 'value': '1'})

    class Meta:
        model = Job
        fields = ('visibility', 'style_weight')


class UpdateVisiblityJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('visibility',)


class UpdateInputImageForm(forms.ModelForm):
    class Meta:
        model = InputImage
        fields = ('visibility', 'title', 'description',
                  'public_domain', 'copyright_notice',)
