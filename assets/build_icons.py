try:
    import Image
except ImportError:
    try:
        from PIL import Image
    except ImportError as exc:
        raise Exception("Can't import PIL or PILLOW. Install one.") from exc


def build_icon(final_width, xray, incognito):
    xray = prepare_xray(final_width, xray)
    incognito = prepare_incognito(incognito)

    xray_border_size = 9

    logo_size = get_logo_size(incognito, xray, xray_border_size)

    icon = Image.new("RGB", logo_size, "white")
    paste_icon_part(icon, incognito, vertical_position=0)
    paste_icon_part(icon, xray, vertical_position=incognito.height + xray_border_size)

    icon = icon.resize((final_width, final_width), Image.BICUBIC)
    icon.save("dicognito_" + str(icon.width) + ".png")


def paste_icon_part(icon, part, vertical_position):
    icon.paste(part, ((icon.width - part.width) // 2, vertical_position), part)


def prepare_xray(final_width, xray):
    xray_bounds = get_xray_bounds(final_width)
    xray = xray.crop(xray_bounds)
    return xray


def get_xray_bounds(final_width):
    if final_width > 100:
        xray_left = 112
        xray_top = 253
        xray_height = 298
    else:
        xray_left = 148
        xray_top = 290
        xray_height = 225

    xray_width = xray.width - xray_left * 2

    return (xray_left, xray_top, xray_left + xray_width, xray_top + xray_height)


def prepare_incognito(incognito):
    incognito_bounds = (40, 15, 640, 500)
    incognito = incognito.crop(incognito_bounds)

    new_width = 262
    new_height = int(1.0 * incognito.height / incognito.width * new_width)

    incognito = incognito.resize((new_width, new_height), Image.BICUBIC)
    return incognito


def get_logo_size(incognito, xray, xray_border_size):
    height = incognito.height + xray.height + 2 * xray_border_size
    width = xray.width

    largest_dimension = max(width, height)
    return (largest_dimension, largest_dimension)


incognito = Image.open("noun_Incognito_7572.png")
xray = Image.open("noun_Radiology_1777366.png")


for final_width in [512, 256, 128, 64, 48, 32, 16]:
    build_icon(final_width, xray, incognito)
