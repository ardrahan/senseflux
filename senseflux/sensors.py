

def three_volt_range(voltage: float) -> int:
    """Returns (int) 0 - 100 based on ratio from 0.0 to 3.0 volts"""
    return int((voltage / 3.0) * 100)


def voltage_to_temperature(voltage: float, units='C'):
    if units == 'C':
        return voltage * 41.67 - 40
    elif units == 'F':
        return voltage * 75.006 - 40
    else:
        raise AttributeError('Units must be either C or F')


def fields_to_values(updates: []) -> []:
    ret = []
    for update in updates:
        ret_u = {'created_at': update['created_at']}
        # fiter out fields
        fields = {k: v for k, v in update.items() if 'field' in k}
        for k, v in fields.items():
            f = field_lookup(k)
            adjval = None

            if f == 'SoilTemperature':
                adjval = voltage_to_temperature(v)
            elif f == 'Battery':
                adjval = v
            else:
                adjval = three_volt_range(v)

            ret_u[f] = adjval
        ret.append(ret_u)
    return ret


def field_lookup(field: str) -> str:
    if field == 'field1':
        return 'Humidity'
    if field == 'field2':
        return 'SoilTemperature'
    if field == 'field3':
        return 'SoilMoisture'
    if field == 'field4':
        return 'Darkness'
    if field == 'field5':
        return 'Battery'
