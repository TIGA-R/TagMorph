from collections import namedtuple  
Audit = namedtuple('Audit', ['tagProvider', 'tableName', 'suffix', 'updateColumn'])  
auditList = [  
Audit('SouthControl', 'south_opc_tags', '.OpcItemPath', 'original_dev'),  
Audit('SouthModified', 'south_opc_tags', '.OpcItemPath', 'modified_dev'),  
Audit('SouthControl', 'south_expr_tags', '.expression', 'original_dev'),  
Audit('SouthModified', 'south_expr_tags', '.expression', 'modified_dev'),  
Audit('NorthControl', 'north_opc_tags', '.OpcItemPath', 'original_dev'),  
Audit('NorthModified', 'north_opc_tags', '.OpcItemPath', 'modified_dev'),  
Audit('NorthControl', 'north_expr_tags', '.expression', 'original_dev'),  
Audit('NorthModified', 'north_expr_tags', '.expression', 'modified_dev'),  
]  
  
for audit in auditList:  
    AuditUpdate.Audit(audit.tagProvider, audit.tableName, suffix=audit.suffix).audit(audit.updateColumn)  
    print('%s | %s | %s | %s |> Completed'%audit)
