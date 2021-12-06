socket_data = {
    "resourceType": "Bundle",
    "entry": [
        {
            "fullUrl": "http://localhost:8001/api_fhir_r4/Claim/EA07F16E-1556-4BA6-95AB-38784D058994",
            "resource":     {
    "resourceType": "Claim",
    "id": "1",
    "identifier": [
        {
            "type": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                        "code": "UUID"
                    }
                ]
            },
            "value": "62F0094D-F273-4252-8B51-A82F4D251F1E"
        },
        {
            "type": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                        "code": "Code"
                    }
                ]
            },
            "value": "CID00001"
        }
    ],
    "status": "active",
    "type": {
        "coding": [
            {
                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/claim-visit-type",
                "code": "O",
                "display": "Other"
            }
        ]
    },
    "use": "claim",
    "patient": {
        "reference": "#Patient/47",
        "type": "Patient",
        "identifier": {
            "type": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                        "code": "ACSN"
                    }
                ]
            },
            "value": "47"
        },
        "display": "105000002"
    },
    "billablePeriod": {
        "start": "2021-03-03",
        "end": "2021-03-03"
    },
    "created": "2021-03-03",
    "enterer": {
        "reference": "#Practitioner/16",
        "type": "Practitioner",
        "identifier": {
            "type": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                        "code": "ACSN"
                    }
                ]
            },
            "value": "16"
        },
        "display": "VIDS0011"
    },
    "provider": {
        "reference": "#Organisation/18",
        "type": "Organisation",
        "identifier": {
            "type": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                        "code": "ACSN"
                    }
                ]
            },
            "value": "18"
        },
        "display": "VIDS001"
    },
    "priority": {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                "code": "normal",
                "display": "Normal"
            }
        ]
    },
    "diagnosis": [
        {
            "sequence": 1,
            "diagnosisCodeableConcept": {
                "coding": [
                    {
                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/diagnosis-ICD10-level1",
                        "code": "A02",
                        "display": "Other salmonella infections"
                    }
                ]
            }
        }
    ],
    "insurance": [
        {
            "sequence": 1,
            "focal": True,
            "coverage": {
                "reference": "Coverage/32",
                "type": "Coverage",
                "identifier": {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "ACSN"
                            }
                        ]
                    },
                    "value": "32"
                }
            }
        }
    ],
    "item": [
        {
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/claim-item-reference",
                    "valueReference": {
                        "reference": "#Medication/182",
                        "type": "Medication",
                        "identifier": {
                            "type": {
                                "coding": [
                                    {
                                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                        "code": "ACSN"
                                    }
                                ]
                            },
                            "value": "182"
                        }
                    }
                }
            ],
            "sequence": 1,
            "category": {
                "text": "item"
            },
            "productOrService": {
                "text": "0182"
            },
            "quantity": {
                "value": 2.0
            },
            "unitPrice": {
                "value": 10.0,
                "currency": "$"
            }
        },
        {
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/claim-item-reference",
                    "valueReference": {
                        "reference": "#ActivityDefinition/90",
                        "type": "ActivityDefinition",
                        "identifier": {
                            "type": {
                                "coding": [
                                    {
                                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                        "code": "ACSN"
                                    }
                                ]
                            },
                            "value": "90"
                        }
                    }
                }
            ],
            "sequence": 2,
            "category": {
                "text": "service"
            },
            "productOrService": {
                "text": "A1"
            },
            "quantity": {
                "value": 10.0
            },
            "unitPrice": {
                "value": 400.0,
                "currency": "$"
            }
        },
        {
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/claim-item-reference",
                    "valueReference": {
                        "reference": "#ActivityDefinition/86",
                        "type": "ActivityDefinition",
                        "identifier": {
                            "type": {
                                "coding": [
                                    {
                                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                        "code": "ACSN"
                                    }
                                ]
                            },
                            "value": "86"
                        }
                    }
                }
            ],
            "sequence": 3,
            "category": {
                "text": "service"
            },
            "productOrService": {
                "text": "I113"
            },
            "quantity": {
                "value": 55.0
            },
            "unitPrice": {
                "value": 1250.0,
                "currency": "$"
            }
        }
    ],
    "total": {
        "value": 1670.0,
        "currency": "$"
    },
    "contained": [
        {
            "resourceType": "Patient",
            "id": "47",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-is-head",
                    "valueBoolean": False
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-card-issued",
                    "valueBoolean": False
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-group-reference",
                    "valueReference": {
                        "reference": "Group/18",
                        "type": "Group",
                        "identifier": {
                            "type": {
                                "coding": [
                                    {
                                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                        "code": "ACSN"
                                    }
                                ]
                            },
                            "value": "18"
                        }
                    }
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "05AF08B5-6E85-470C-83EC-0EE9370FDF40"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "105000002"
                }
            ],
            "name": [
                {
                    "use": "usual",
                    "family": "Ilina",
                    "given": [
                        "Doni"
                    ]
                }
            ],
            "gender": "female",
            "birthDate": "1993-06-09",
            "address": [
                {
                    "extension": [
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-municipality",
                            "valueString": "Majhi"
                        },
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference",
                            "valueReference": {
                                "reference": "Location/45",
                                "type": "Location",
                                "identifier": {
                                    "type": {
                                        "coding": [
                                            {
                                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                                "code": "ACSN"
                                            }
                                        ]
                                    },
                                    "value": "45"
                                }
                            }
                        }
                    ],
                    "use": "home",
                    "type": "physical",
                    "city": "Radho",
                    "district": "Vida",
                    "state": "Tahida"
                }
            ],
            "photo": [
                {
                    "contentType": "jpg",
                    "url": "http://localhost/photo/Images/Updated//105000002_E00001_20180327_0.0_0.0.jpg",
                    "title": "105000002_E00001_20180327_0.0_0.0.jpg",
                    "creation": "2018-03-27"
                }
            ]
        },
        {
            "resourceType": "Group",
            "id": "18",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/group-address",
                    "valueAddress": {
                        "extension": [
                            {
                                "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-municipality",
                                "valueString": "Majhi"
                            },
                            {
                                "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference",
                                "valueReference": {
                                    "reference": "Location/45",
                                    "type": "Location",
                                    "identifier": {
                                        "type": {
                                            "coding": [
                                                {
                                                    "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                                    "code": "ACSN"
                                                }
                                            ]
                                        },
                                        "value": "45"
                                    }
                                }
                            }
                        ],
                        "use": "home",
                        "type": "physical",
                        "city": "Radho",
                        "district": "Vida",
                        "state": "Tahida"
                    }
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "97BA5232-9054-4D86-B4F2-0E9C4ADF183E"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "10500001"
                }
            ],
            "active": True,
            "type": "Person",
            "actual": True,
            "name": "Ilina",
            "quantity": 2,
            "member": [
                {
                    "entity": {
                        "reference": "Patient/10500001",
                        "type": "Patient"
                    }
                },
                {
                    "entity": {
                        "reference": "Patient/105000002",
                        "type": "Patient"
                    }
                }
            ]
        },
        {
            "resourceType": "Organization",
            "id": "18",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/organization-legal-form",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "CodeSystem/organization-legal-form",
                                "code": "D",
                                "display": "District organization"
                            }
                        ]
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig//StructureDefinition/organization-hf-level",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig//CodeSystem/organization-hf-level",
                                "code": "D",
                                "display": "Dispensary"
                            }
                        ]
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/organization-hf-care-type",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig//CodeSystem/organization-hf-care-type",
                                "code": "O",
                                "display": "Out-patient"
                            }
                        ]
                    }
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "47EC5F9B-97C6-444B-AAD9-2FCCFD4623FA"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "VIDS001"
                }
            ],
            "type": [
                {
                    "coding": [
                        {
                            "code": "prov"
                        }
                    ]
                }
            ],
            "name": "Viru Dispensary",
            "telecom": [
                {
                    "system": "email",
                    "value": "test_email"
                },
                {
                    "system": "phone",
                    "value": "test_phone"
                },
                {
                    "system": "fax",
                    "value": "test_fax"
                }
            ],
            "address": [
                {
                    "extension": [
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig//StructureDefinition/address-location-reference",
                            "valueReference": {
                                "reference": "Organisation/18",
                                "type": "Organisation",
                                "identifier": {
                                    "type": {
                                        "coding": [
                                            {
                                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                                "code": "ACSN"
                                            }
                                        ]
                                    },
                                    "value": "18"
                                }
                            }
                        }
                    ],
                    "type": "physical",
                    "line": [
                        "Uitly road 1"
                    ],
                    "district": "Vida",
                    "state": "Tahida"
                }
            ],
            "contact": [
                {
                    "purpose": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/contactentity-type",
                                "code": "PAYOR"
                            }
                        ]
                    },
                    "name": {
                        "use": "usual",
                        "family": "Duikolau",
                        "given": [
                            "Juolpio"
                        ]
                    }
                },
                {
                    "purpose": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/contactentity-type",
                                "code": "PAYOR"
                            }
                        ]
                    },
                    "name": {
                        "use": "usual",
                        "family": "Duikolau",
                        "given": [
                            "Juolpio"
                        ]
                    }
                }
            ]
        },
        {
            "resourceType": "Practitioner",
            "id": "16",
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "3E385229-DD11-4383-863C-E2FAD1B2380E"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "VIDS0011"
                }
            ],
            "name": [
                {
                    "use": "usual",
                    "family": "Duikolau",
                    "given": [
                        "Juolpio"
                    ]
                }
            ],
            "birthDate": "1977-11-13",
            "qualification": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/practitioner-qualification-type",
                                "code": "CA",
                                "display": "Claim Administrator"
                            }
                        ]
                    }
                }
            ]
        },
        {
            "resourceType": "Medication",
            "id": "182",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/unit-price",
                    "valueMoney": {
                        "value": 10.0,
                        "currency": "$"
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/medication-type",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/medication-item-type",
                                "code": "D",
                                "display": "Drug"
                            }
                        ]
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/medication-frequency",
                    "valueTiming": {
                        "repeat": {
                            "frequency": 1,
                            "period": 0.0,
                            "periodUnit": "d"
                        }
                    }
                },
                {
                    "extension": [
                        {
                            "url": "Gender",
                            "valueUsageContext": {
                                "code": {
                                    "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                                    "code": "gender",
                                    "display": "Gender"
                                },
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "http://hl7.org/fhir/administrative-gender",
                                            "code": "male",
                                            "display": "Male"
                                        },
                                        {
                                            "system": "http://hl7.org/fhir/administrative-gender",
                                            "code": "female",
                                            "display": "Female"
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "url": "Age",
                            "valueUsageContext": {
                                "code": {
                                    "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                                    "code": "age",
                                    "display": "Age"
                                },
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/usage-context-age-type",
                                            "code": "adult",
                                            "display": "Adult"
                                        },
                                        {
                                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/usage-context-age-type",
                                            "code": "child",
                                            "display": "Child"
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "url": "CareType",
                            "valueUsageContext": {
                                "code": {
                                    "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                                    "code": "venue",
                                    "display": "Clinical Venue"
                                },
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                                            "code": "AMB",
                                            "display": "ambulatory"
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/medication-usage-context"
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/medication-level",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/ValueSet/medication-level",
                                "code": "M",
                                "display": "Medication"
                            }
                        ],
                        "text": "Medication"
                    }
                },
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "6B5D76E2-DC28-4B48-8E29-3AC4ABECC929"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "0182"
                }
            ],
            "code": {
                "text": "PARACETAMOL TABS 500 MG"
            },
            "status": "active",
            "form": {
                "text": "1000 TABLETS"
            },
            "amount": {
                "numerator": {
                    "value": 1000.0
                }
            }
        },
        {
            "resourceType": "ActivityDefinition",
            "id": "90",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/unit-price",
                    "valueMoney": {
                        "value": 400.0,
                        "currency": "$"
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/activity-definition-level",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/ValueSet/activity-definition-level",
                                "code": "D",
                                "display": "Day of stay"
                            }
                        ],
                        "text": "Day of stay"
                    }
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "72A229BA-3F4E-4E6F-B55C-23A488A13820"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "A1"
                }
            ],
            "name": "A1",
            "title": "General Consultation",
            "status": "active",
            "date": "2017-01-01T00:00:00",
            "useContext": [
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "gender",
                        "display": "Gender"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/administrative-gender",
                                "code": "female",
                                "display": "Female"
                            }
                        ],
                        "text": "Male or Female"
                    }
                },
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "age",
                        "display": "Age Range"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/usage-context-age-type",
                                "code": "adult",
                                "display": "Adult"
                            }
                        ],
                        "text": "Adult or Child"
                    }
                },
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "venue",
                        "display": "Clinical Venue"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/2.1.0/CodeSystem-v3-ActCode.html",
                                "code": "AMB",
                                "display": "ambulatory"
                            }
                        ],
                        "text": "ambulatory"
                    }
                }
            ],
            "topic": [
                {
                    "coding": [
                        {
                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/activity-definition-service-type.html",
                            "code": "P",
                            "display": "Preventive"
                        }
                    ]
                }
            ],
            "timingTiming": {
                "repeat": {
                    "frequency": 1,
                    "period": 0.0,
                    "periodUnit": "d"
                }
            }
        },
        {
            "resourceType": "ActivityDefinition",
            "id": "86",
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/unit-price",
                    "valueMoney": {
                        "value": 1250.0,
                        "currency": "$"
                    }
                },
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/activity-definition-level",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/ValueSet/activity-definition-level",
                                "code": "S",
                                "display": "Simple Service"
                            }
                        ],
                        "text": "Simple Service"
                    }
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "UUID"
                            }
                        ]
                    },
                    "value": "D5B1C425-093C-49E1-9E0F-CF1B0DA5CB60"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                "code": "Code"
                            }
                        ]
                    },
                    "value": "I113"
                }
            ],
            "name": "I113",
            "title": "BLOOD SUGAR-RANDOM OR FASTING",
            "status": "active",
            "date": "2017-01-01T00:00:00",
            "useContext": [
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "gender",
                        "display": "Gender"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/administrative-gender",
                                "code": "male",
                                "display": "Male"
                            }
                        ],
                        "text": "Male or Female"
                    }
                },
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "age",
                        "display": "Age Range"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/usage-context-age-type",
                                "code": "child",
                                "display": "Child"
                            }
                        ],
                        "text": "Adult or Child"
                    }
                },
                {
                    "code": {
                        "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
                        "code": "venue",
                        "display": "Clinical Venue"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/2.1.0/CodeSystem-v3-ActCode.html",
                                "code": "AMB",
                                "display": "ambulatory"
                            },
                            {
                                "system": "http://terminology.hl7.org/2.1.0/CodeSystem-v3-ActCode.html",
                                "code": "IMP",
                                "display": "IMP"
                            }
                        ],
                        "text": "ambulatory or IMP"
                    }
                }
            ],
            "topic": [
                {
                    "coding": [
                        {
                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/activity-definition-service-type.html",
                            "code": "P",
                            "display": "Preventive"
                        }
                    ]
                }
            ],
            "timingTiming": {
                "repeat": {
                    "frequency": 1,
                    "period": 0.0,
                    "periodUnit": "d"
                }
            }
        }
    ]
}
                                }
    ]
}
