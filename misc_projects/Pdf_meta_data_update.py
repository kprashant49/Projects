import pikepdf

input_path  = r"C:\Users\kpras\Desktop\Employment_Contract_Prashant Kumar.pdf"
output_path = r"C:\Users\kpras\Desktop\Employment_Contract_Prashant Kumar.pdf"

with pikepdf.open(input_path, allow_overwriting_input=True) as pdf:
    with pdf.open_metadata() as meta:
        meta["xmp:CreateDate"] = "2026-03-17T13:21:14+05:30"   #  IST timezone
        meta["xmp:ModifyDate"] = "2026-03-17T13:21:14+05:30"   #  IST timezone
        meta["pdf:Producer"]   = "Microsoft® Word for Microsoft 365"

    # PDF docinfo timezone format: +HH'mm'
    pdf.docinfo["/CreationDate"] = "D:20260317132114+05'30'"    #  IST timezone
    pdf.docinfo["/ModDate"]      = "D:20260317132114+05'30'"    #  IST timezone
    pdf.docinfo["/Producer"]     = "Microsoft® Word for Microsoft 365"

    pdf.save(output_path)

print("Done! Metadata updated.")