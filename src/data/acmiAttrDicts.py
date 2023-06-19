acmi_old_obj_to_attr = {
    "T=": -1,
    "IAS": None,
    "PilotHeadRoll=": None,
    "PilotHeadPitch=": None,
    "PilotHeadYaw=": None,
    "AOA=": None,
    "AOAUnits=": None,
}
acmi_new_obj_to_attr = {
    "T=": -1,
    "Type=": "type",
    "Name=": "name",
    "Pilot=": "pilot",
    "Color=": "color",
    "Group=": "group",
    "Coalition=": "coalition",
    "Country=": "country",
}
acmi_obj_to_attr_all = acmi_new_obj_to_attr | acmi_old_obj_to_attr
acmi_global_to_attr = {
    "0,ReferenceTime=": "mission_date",
    "0,RecordingTime=": "record_date",
    "0,Title=": "mission_title",
    "0,DataRecorder=": "recorder",
    "0,DataSource=": "source",
    "0,Author=": "author",
    "0,Comments=": "comments",
    "0,ReferenceLongitude=": "longitude_reference",
    "0,ReferenceLatitude=": "latitude_reference",
    "0,Category=": "category",
}
