import json

def calculatePriceAverage(price30Days):
    price_elements = price30Days["vdate"]
    volume_sum = 0
    oi_sum = 0

    for price_element in price_elements:
        volume_sum += float(price_element["futureVolume"])
        oi_sum += float(price_element["futureOi"])

    average_volume = volume_sum / len(price_elements)
    average_oi = oi_sum / len(price_elements)

    return average_volume, average_oi

