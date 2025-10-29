
# import testforms
import forms
# import incShip.load_init_data.load_HBL as load_HBL
# import incShip.load_init_data.load_Invoices as load_Invoices 

# def LoadAdmin(parent):
def LoadAdmin():
    # return redirect('/admin/')
    return



#########################################################################
#########################################################################


FormNameToURL_Map = {}
# FormNameToURL_Map['menu Argument'.lower()] = (url, view)
# FormNameToURL_Map['l10-wics-uadmin'.lower()] = (None, fnWICSuserForm)
# FormNameToURL_Map['l6-wics-uadmin'.lower()] = FormNameToURL_Map['l10-wics-uadmin']
FormNameToURL_Map['django-admin'.lower()] = (None, LoadAdmin)

# FormNameToURL_Map['test01'.lower()] = (None, testforms.Test01)
# FormNameToURL_Map['test02'.lower()] = (None, testforms.Test02)
# FormNameToURL_Map['test02'.lower()] = (None, testforms.refsForm)
# FormNameToURL_Map['test03'.lower()] = (None, testforms.Test03)

FormNameToURL_Map['HBLForm'.lower()] = (None, forms.HBLForm)

FormNameToURL_Map['InvoiceForm'.lower()] = (None, None)
FormNameToURL_Map['InvoicesNotsubmitted'.lower()] = (None, None)

FormNameToURL_Map['refsForm'.lower()] = (None, None)
FormNameToURL_Map['newref'.lower()] = (None, None)

# FormNameToURL_Map['init-load-HBL-00'.lower()] = (None, load_HBL.LoadHBL)
# FormNameToURL_Map['init-load-Inv-00'.lower()] = (None, load_Invoices.LoadInvoices)
