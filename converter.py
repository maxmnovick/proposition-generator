# converter.py

def convert_dict_to_list(dict, desired_order=[]):

    dict_list = []

    for key in desired_order:
        val = dict[key]
        dict_list.append(val)

    # add remaining in the order they come
    for key, val in dict.items():
        # if not already added
        if key not in desired_order:
            dict_list.append(val)

    return dict_list


def convert_dicts_to_lists(all_consistent_stat_dicts, desired_order=[]):

    dict_lists = []

    for dict in all_consistent_stat_dicts:

        dict_list = convert_dict_to_list(dict, desired_order)

        dict_lists.append(dict_list)
        
    return dict_lists