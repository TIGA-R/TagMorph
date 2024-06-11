
"""
The following represents the base process steps used in the original implementation of the object modification script. This is not intended to run -> just a placeholder
"""
udt_base_process_steps = [
    udt_name_set_addition,
    type_prefix_removal,
    partial(parameter_change, parameter_dict, '~', '_t_'),
    partial(alarm_udt_base_tracking, alarm_udt_base_nodes, alarm_udt_base_node),
    namespace_parameter_addition,
    partial(udt_count_update, udt_count),
    partial(parameter_remove, '_Historize'),
]

udt_inst_process_steps = [
    partial(name_addition, tag_name_set),
    type_prefix_removal,
    type_case_correction,
    partial(parameter_change, inst_parameter_dict, '~', '_t_'),
    partial(udt_count_update, udt_count),
]

atomic_process_steps = [
    partial(alarm_count, alarm_count_dict),
    partial(expression_format, expression_set),
    history_update,
    update_opc_path,
    partial(opc_path_change, '~', '_t_'),
]

folder_node = [
    partial(name_addition, folder_name_set),
]
