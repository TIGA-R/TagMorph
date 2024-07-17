from functools import partial
import pathlib
from analyze.relationships import SqliteDatatype, atom_tag_gen_build, build_child_parent, build_test_database
from parse.node_strategies import alarm_enabled_parameter_update, atom_tag_dict_build, binding_change, expression_format, history_update, namespace_parameter_addition, opc_path_change, parameter_change, parameters_remove, type_case_wrapper, type_dict_build, type_prefix_removal, udt_instance_dict_build, update_opc_path
from parse.tag_dataclasses import ValueSource
from parse.tag_process import TagProcessor  

path = str(pathlib.Path(__file__).parent.resolve()) + '/tests/json/7-16-2024/'
single_site_file = 'simple single site tags.json'
original_single_site_file = 'single site tags.json'
single_well_file = 'single well tags.json'
south_site_file = 'south tags.json'
north_site_file = 'north tags.json'

def build_audit_tag_table(
    atomic_value_source: ValueSource|list[ValueSource],
    source_file: str,
    area: str,
    db: str,
    table: str,
    columns: dict[str, SqliteDatatype]={'original': 'TEXT', 'modified': 'TEXT'},
):
    type_dict = {}
    name_dict = {}
    type_case_correction = type_case_wrapper()
    missing_udt_dict = {}
    import time
    start = time.time()
    atom_dict = {}
    udt_inst_dict = {}

    with TagProcessor(
        source_file,
        area,
        atomic_process_steps = [
            partial(atom_tag_dict_build, atom_dict, atomic_value_source),
            type_prefix_removal,
        ],
        udtInstance_process_steps = [
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(udt_instance_dict_build, udt_inst_dict),
            partial(type_dict_build, name_dict, type_dict),
        ],
        udtType_process_steps = [
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(type_dict_build, name_dict, type_dict),
        ],
    ) as processor:
        processor.process()

    mid = time.time()

    pc_dict = build_child_parent(type_dict, name_dict)


    atom_tag_gen = atom_tag_gen_build(atom_dict, udt_inst_dict, pc_dict)
    
    build_test_database(
    file_path=db,
    table_name=table,
    data_generator=atom_tag_gen,
    audit_columns=columns,
    ) 

    finish = time.time()
    print(f"Time to process: {mid-start} s")
    print(f"Time to map: {finish-mid} s")

parameter_change_dict = {
    '~': '_t_',
    'Pump N_12': '_p_Pump N_12',
    'Pump N_2': '_p_Pump N_2',
    'Pump N_3': '_p_Pump N_3',
    'Tank N_4': '_p_Tank N_4',
    'Vessel N_3': '_p_Vessel N_3',
    'Well_n2': '_p_Well_n2',
    'Well_n4': '_p_Well_n4',
    '_Address Buffer': '_p_Address Buffer',
    '_AppConfig': '_e_AppConfig',
    '_Choke': '_p_Choke',
    '_Choke Valve': '_p_Choke Valve',
    '_Comp Num': '_e_Comp Num',
    '_Cushion': '_p_Cushion',
    '_Double': '_e_Double',
    '_Flare': '_e_Flare',
    '_Flare Num': '_e_Flare Num',
    '_Flow Rate': '_t_Flow Rate',
    '_Gas Lift': '_p_Gas Lift',
    '_HP': '_p_HP',
    '_Heater': '_p_Heater',
    '_Heater Num': '_e_Heater Num',
    '_Jump': '_p_Jump',
    '_LP': '_p_LP',
    '_Lact Num': '_e_Lact Num',
    '_Meter Flow Rate Tagpath': '_t_Meter Flow Rate Tagpath',
    '_Meter Flow Rate': '_t_Meter Flow Rate',
    '_Meter Num': '_e_Meter Num',
    '_PID Num': '_e_PID Num',
    '_PMeq': '_e_PMeq',
    '_Pmeq': '_e_PMeq',
    '_Pump Adder': '_p_Pump Adder',
    '_Pump Num': '_e_Pump Num',
    '_Reg Space': '_e_Reg Space',
    '_Tank N_2': '_p_Tank N2',
    '_Tank Num': '_e_Tank Num',
    '_Tank Register': '_p_Tank Register',
    '_Tank Type': '_p_Tank Type',
    '_User Data': '_e_User Data',
    '_VRU': '_p_VRU',
    '_Valve Num': '_e_Valve Num',
    '_Vessel Num': '_e_Vessel Num',
    '_Volume Accumulated': '_t_Volume Accumulated',
    '_Volume Today': '_t_Volume Today',
    '_Volume Yesterday': '_t_Volume Yesterday',
    '_Water': '_p_Water',
    '_Well Num': '_e_Well Num',
    '_SP Adder': '_p_SP Adder',
    '_Separator Adder': '_p_Separator Adder',
    '__Abs Tank Num': '_e_Abs Tank Num',
    '__CCF Factor': '_t_CCF Factor',
    '__CPL Factor': '_t_CPL Factor',
    '__CTL Factor': '_t_CTL Factor',
    '__Casing Pressure': '_t_Casing Pressure',
    '__Closing Meter Reading': '_t_Closing Meter Reading',
    '__Contract Hour': '_t_Contract Hour',
    '__Coriolis Meter Num': '_e_Coriolis Meter Num',
    '__Corrected Gravity': '_t_Corrected Gravity',
    '__Density Avg Prev Mnth': '_t_Density Avg Prev Mnth',
    '__ESD': '_t_ESD',
    '__FireLoop': '_t_FireLoop',
    '__Flare Adder': '_p_Flare Adder',
    '__Flow Rate': '_t_Flow Rate',
    '__From Location': '_t_From Location',
    '__Gate ESD': '_t_Gate ESD',
    '__Gross Standard Volume Accumulated': '_t_Gross Standard Volume Accumulated',
    '__Gross Standard Volume Current Hour': '_t_Gross Standard Volume Current Hour',
    '__Gross Standard Volume Current Month': '_t_Gross Standard Volume Current Month',
    '__Gross Standard Volume Current Week': '_t_Gross Standard Volume Current Week',
    '__Gross Standard Volume Previous Hour': '_t_Gross Standard Volume Previous Hour',
    '__Gross Standard Volume Previous Month': '_t_Gross Standard Volume Previous Month',
    '__Gross Standard Volume Prev Month': '_t_Gross Standard Volume Prev Month',
    '__Gross Standard Volume Previous Week': '_t_Gross Standard Volume Previous Week',
    '__Gross Standard Volume Today': '_t_Gross Standard Volume Today',
    '__Gross Standard Volume Yesterday': '_t_Gross Standard Volume Yesterday',
    '__HP': '_p_HP',
    '__Heater Jump3': '_p_Heater Jump3',
    '__Indicated Volume Accumulated': '_t_Indicated Volume Accumulated',
    '__Indicated Volume Current Hour': '_t_Indicated Volume Current Hour',
    '__Indicated Volume Current Month': '_t_Indicated Volume Current Month',
    '__Indicated Volume Current Week': '_t_Indicated Volume Current Week',
    '__Indicated Volume Previous Hour': '_t_Indicated Volume Previous Hour',
    '__Indicated Volume Previous Month': '_t_Indicated Volume Previous Month',
    '__Indicated Volume Previous Week': '_t_Indicated Volume Previous Week',
    '__Indicated Volume Today': '_t_Indicated Volume Today',
    '__Indicated Volume Yesterday': '_t_Indicated Volume Yesterday',
    '__Interface Level': '_t_Interface Level',
    '__LACT PSI (Live)': '_t_LACT PSI Live',
    '__LACT Pump Dry Run': '_t_LACT Pump Dry Run',
    '__LACT Temp (Live)': '_t_LACT Temp Live',
    '__LSH': '_t_LSH',
    '__LSHH': '_t_LSHH',
    '__LSHH Setpoint': '_t_LSHH Setpoint',
    '__Line Pressure': '_t_Line Pressure',
    '__Local ESD': '_t_Local ESD',
    '__Meter 3 Adder': '_p_Meter 3 Adder',
    '__Meter Adder': '_p_Meter Adder',
    '__Meter Factor': '_p_Meter Factor',
    '__Meter Name': '_t_Meter Name',
    '__Meter Num': '_e_Meter Num',
    '__Meter Observed Density': '_t_Meter Observed Density',
    '__Net Volume Accumulated': '_t_Net Volume Accumulated',
    '__Net Volume Accumulated Midnight': '_t_Net Volume Accumulated Midnight',
    '__Net Volume Current Hour': '_t_Net Volume Current Hour',
    '__Net Volume Current Month': '_t_Net Volume Current Month',
    '__Net Volume Current Week': '_t_Net Volume Current Week',
    '__Net Volume Previous Hour': '_t_Net Volume Previous Hour',
    '__Net Volume Previous Month': '_t_Net Volume Previous Month',
    '__Net Volume Previous Week': '_t_Net Volume Previous Week',
    '__Net Volume Today': '_t_Net Volume Today',
    '__Net Volume Yesterday': '_t_Net Volume Yesterday',
    '__Net Volume Yesterday Midnight': '_t_Net Volume Yesterday Midnight',
    '__Obs Gravity': '_t_Obs Gravity',
    '__Obs Temp': '_t_Obs Temp',
    '__Opening Meter Reading': '_t_Opening Meter Reading',
    '__Panel ESD': '_t_Panel ESD',
    '__Parameter Adder': '_p_Parameter Adder',
    '__Remote ESD': '_t_Remote ESD',
    '__SP Adder': '_p_SP Adder',
    '__SW (Live)': '_t_SW Live',
    '__SW Avg Prev Mnth': '_t_SW Avg Prev Mnth',
    '__SW Correction Factor': '_t_SW Correction Factor',
    '__SW Volume Prev Mnth': '_t_SW Volume Prev Mnth',
    '__Separator Adder': '_p_Separator Adder',
    '__Serial Number': '_t_Serial Number',
    '__Statement Volume Prev Mnth': '_t_Statement Volume Prev Mnth',
    '__Temperature': '_t_Temperature',
    '__Ticket Number': '_t_Ticket Number',
    '__Top Level': '_t_Top Level',
    '__Total Num': '_p_Total Num',
    '__Total_X2': '_t_TotalX2',
    '__Total_X4': '_t_TotalX4',
    '__Total_X5': '_t_TotalX5',
    '__Tubing Pressure': '_t_Tubing Pressure',
    '__Turbine Meter Num': '_t_Turbine Meter Num',
    '__Volume Accumulated': '_t_Volume Accumulated',
    '__Volume Today': '_t_Volume Today',
    '__Volume Yesterday': '_t_Volume Yesterday',
    '__Weighted Average Pressure Prev Mnth': '_t_Weighted Average Pressure Prev Mnth',
    '__Weighted Average Temperature Prev Mnth': '_t_Weighted Average Temperature Prev Mnth',
    '__': '_',
}

if __name__ == '__main__':
    type_case_correction = type_case_wrapper()
    missing_udt_dict = {}
    import time
    start = time.time()
    # build_audit_tag_table(
    #     atomic_value_source='expr',
    #     source_file=path+south_site_file,
    #     area='South',
    #     db=path+'july_16_2024_tag_audit',
    #     table='south_expr_tags',
    #     columns={
    #         'original_local': 'TEXT',
    #         'modified_local': 'TEXT',
    #         'original_dev': 'TEXT',
    #         'modified_dev': 'TEXT',
    #         'original_prod': 'TEXT',
    #         'modified_prod': 'TEXT',
    #     },
    # )
    # build_audit_tag_table(
    #     atomic_value_source='opc',
    #     source_file=path+south_site_file,
    #     area='South',
    #     db=path+'july_16_2024_tag_audit',
    #     table='south_opc_tags',
    #     columns={
    #         'original_local': 'TEXT',
    #         'modified_local': 'TEXT',
    #         'original_dev': 'TEXT',
    #         'modified_dev': 'TEXT',
    #         'original_prod': 'TEXT',
    #         'modified_prod': 'TEXT',
    #     },
    # )

    with TagProcessor(
        path+south_site_file,
        'South',
        atomic_process_steps = [
            partial(opc_path_change, parameter_change_dict),
            partial(binding_change, parameter_change_dict),
            partial(parameters_remove, ['_Historize']),
            update_opc_path,
            namespace_parameter_addition,
            alarm_enabled_parameter_update,
            expression_format,
            history_update,
            type_prefix_removal,
        ],
        udtInstance_process_steps = [
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(parameters_remove, [
                '_Historize',
                '_Address Buffer Description',
                '__Abs Tank Num Description',
                '__Total Num Description',
                '__Meter Num Description',
                '_Tank Type Description',
                '_Tank Num Description',
                '_Tank N_2 Description',
                '_Water Description',
                '_LP Description',
                '_Choke Valve Description',
                'Pump N_12 Description',
                'Pump N_2 Description',
                'Pump N_3 Description',
                'Tank N_4 Description',
                'Vessel N_3 Description',
                'Well_n2_Description',
                'Well_n4_Description',
            ]),
            partial(parameter_change, parameter_change_dict),
            partial(opc_path_change, parameter_change_dict),
            partial(binding_change, parameter_change_dict),
            alarm_enabled_parameter_update,
            update_opc_path,
            namespace_parameter_addition,
            expression_format,
            history_update,
        ],
        udtType_process_steps = [
            type_prefix_removal,
            partial(type_case_correction, missing_udt_dict),
            partial(parameters_remove, [
                '_Historize',
                '_Address Buffer Description',
                '__Abs Tank Num Description',
                '__Total Num Description',
                '__Meter Num Description',
                '_Tank Type Description',
                '_Tank Num Description',
                '_Tank N_2 Description',
                '_Water Description',
                '_LP Description',
                '_Choke Valve Description',
                'Pump N_12 Description',
                'Pump N_2 Description',
                'Pump N_3 Description',
                'Tank N_4 Description',
                'Vessel N_3 Description',
                'Well_n2_Description',
                'Well_n4_Description',
            ]),
            partial(parameter_change, parameter_change_dict),
            partial(opc_path_change, parameter_change_dict),
            partial(binding_change, parameter_change_dict),
            update_opc_path,
            alarm_enabled_parameter_update,
            namespace_parameter_addition,
            expression_format,
            history_update,
        ],
    ) as processor:
        processor.process()
        processor.to_file(path + 'south_prod_mod_2.json')
    mid = time.time()

    finish = time.time()
    print(f"Time to process: {mid-start} s")
    print(f"Time to map: {finish-mid} s")
