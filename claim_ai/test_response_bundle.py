adjudication_bundle = {
    'resourceType': 'AdjudicationBundle',
    'entry': [
        {
                "resourceType": "ClaimResponse",
                "created": "2020-11-15",
                "id": "C670E61A-36F1-4F70-A5D2-6CE2C20457F6",
                "item": [
                    {
                        "adjudication": [
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 14.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "2"
                                        }
                                    ],
                                    "text": "entered"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 13.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "4"
                                        }
                                    ],
                                    "text": "checked"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 12.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "8"
                                        }
                                    ],
                                    "text": "processed"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 12.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "16"
                                        }
                                    ],
                                    "text": "valuated"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            }
                        ],
                        "extension": [
                            {
                                "url": "Medication",
                                "valueReference": {
                                    "reference": "Medication/4DAFEF84-7AFA-47C6-BB51-B6D5511A8AF9"
                                }
                            }
                        ],
                        "itemSequence": 1,
                        "noteNumber": [
                            1
                        ]
                    },
                    {
                        "adjudication": [
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 400.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "2"
                                        }
                                    ],
                                    "text": "entered"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 400.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "4"
                                        }
                                    ],
                                    "text": "checked"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "category": {
                                    "coding": [
                                        {
                                            "code": "8"
                                        }
                                    ],
                                    "text": "processed"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            },
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 400.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "16"
                                        }
                                    ],
                                    "text": "valuated"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": "0"
                                        }
                                    ]
                                },
                                "value": 1.0
                            }
                        ],
                        "extension": [
                            {
                                "url": "ActivityDefinition",
                                "valueReference": {
                                    "reference": "Medication/48DB6423-E696-45D9-B76E-CA1B7C57D738"
                                }
                            }
                        ],
                        "itemSequence": 2,
                        "noteNumber": [
                            2
                        ]
                    }
                ],
                "outcome": "valuated",
                "patient": {
                    "reference": "Patient/80DB8910-8D30-4072-B92D-D3F8E74BB17A"
                },
                "processNote": [
                    {
                        "number": 1,
                        "text": "P"
                    },
                    {
                        "number": 2,
                        "text": "P"
                    }
                ],
                "requestor": {
                    "reference": "HealthcareService/64D5D616-ED4C-4DAC-A87A-19A7CAF01259"
                },
                "status": "Not Selected",
                "total": [
                    {
                        "amount": {
                            "currency": "$",
                            "value": 410.0
                        },
                        "category": {
                            "coding": [
                                {
                                    "code": "submitted",
                                    "display": "Submitted Amount",
                                    "system": "http://terminology.hl7.org/CodeSystem/adjudication.html"
                                }
                            ],
                            "text": "Claimed"
                        }
                    }
                ],
                "type": {
                    "text": "O"
                },
                "use": "claim"
            }
    ]
}