from typing import Dict
import os


def three_volt_range(voltage: float) -> float:
    """Returns (int) 0 - 100 based on ratio from 0.0 to 3.0 volts"""
    return float((voltage / 3.0) * 100)


def voltage_to_temperature(voltage: float, units='C'):
    if units == 'C':
        return voltage * 41.67 - 40
    elif units == 'F':
        return voltage * 75.006 - 40
    else:
        raise AttributeError('Units must be either C or F')


def fields_to_values(updates: [], field_map: Dict[str, str]) -> []:
    ret = []
    for update in updates:
        ret_u = {'created_at': update['created_at']}
        # fiter out fields
        fields = {k: v for k, v in update.items() if 'field' in k}
        for k, v in fields.items():
            f = field_map[k]

            if f == 'SoilTemperature':
                adjval = voltage_to_temperature(v)
            elif f == 'Battery':
                adjval = v
            else:
                adjval = three_volt_range(v)


            ret_u[f] = adjval
        ret.append(ret_u)
    return ret


def field_lookup(defaults: Dict[str, str]) -> Dict[str, str]:
    fields = {}
    for i in range(1, 6):
        ef = f'FIELD{i}'
        f_name = f'field{i}'
        if ef in os.environ:
            fields[f_name] = os.environ[ef]
        else:
            fields[f_name] = defaults[f_name]
    return fields
