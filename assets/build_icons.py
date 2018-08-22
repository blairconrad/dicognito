try:
    import Image
    import ImageDraw
except:
    try:
        from PIL import Image
        from PIL import ImageDraw
    except:
        raise Exception("Can't import PIL or PILLOW. Install one.")

incognito = Image.open('noun_Incognito_7572.png')
xray = Image.open('noun_Radiology_1777366.png')


def build_icon(size):

    if (size > 100):
        xray_left = 112
        xray_top = 253
        xray_height = 298
    else:
        xray_left = 148
        xray_top = 290
        xray_height = 225

    xray_width = xray.width - xray_left * 2
    xray_top_part = xray.crop((xray_left, xray_top, xray_left +
                               xray_width, xray_top + xray_height))

    backed_xray = Image.new('RGB', xray_top_part.size, 'white')
    backed_xray.paste(xray_top_part, (0, 0), xray_top_part)

    incognito_left = 40
    incognito_top = 15
    incognito_right = incognito.width - 60
    incognito_bottom = 500
    incognito_cropped = incognito.crop(
        (incognito_left, incognito_top, incognito_right, incognito_bottom))

    backed_incognito_cropped = Image.new(
        'RGB', incognito_cropped.size, 'white')
    backed_incognito_cropped.paste(
        incognito_cropped, (0, 0), incognito_cropped)

    new_width = 262
    new_height = int(1.0 * backed_incognito_cropped.height /
                     backed_incognito_cropped.width * new_width)

    backed_incognito_resized = backed_incognito_cropped.resize(
        (new_width, new_height), Image.BICUBIC)

    # backed_incognito_resized.show()
    gap_size = 9
    bottom_padding_size = gap_size

    logo_height = backed_xray.height + \
        backed_incognito_resized.height + gap_size + bottom_padding_size
    logo_width = backed_xray.width

    logo_size = max(logo_width, logo_height)

    logo = Image.new(backed_xray.mode, (logo_size, logo_size), 'white')
    logo.paste(backed_incognito_resized,
               ((logo.width - backed_incognito_resized.width) / 2, 0))
    logo.paste(backed_xray, ((logo.width - backed_xray.width) /
                             2, backed_incognito_resized.height + gap_size))

    logo.resize((size, size), Image.BICUBIC).save(
        'dicognito_' + str(size) + '.png')


for size in [512, 256, 128, 64, 48, 32, 16]:
    build_icon(size)
