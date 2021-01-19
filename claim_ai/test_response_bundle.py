adjudication_bundle = {
    'resourceType': 'AdjudicationBundle',
    'entry': [
        {
                "resourceType": "ClaimResponse",
                "status": "Not Selected",
                "type": {
                        "text": "O"
                },
                "patient": {
                    "reference": "105000002/CB8497C2-44E6-4E55-97B5-A88B6C3DEDB3"
                },
                "created": "2020-11-15",
                "insurer": {
                    "reference": "Organization/openIMIS-Claim-AI"
                },
                "id": "C670E61A-36F1-4F70-A5D2-6CE2C20457F6",
                "request": {
                    "reference": "Claim/C670E61A-36F1-4F70-A5D2-6CE2C20457F6"
                },
                "item": [
                    {
                        "adjudication": [
                            {
                                "amount": {
                                    "currency": "$",
                                    "value": 13.0
                                },
                                "category": {
                                    "coding": [
                                        {
                                            "code": "-2",
                                        }
                                    ],
                                    "text": "AI"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": 0
                                        }
                                    ],
                                    "text": "accepted"
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
                                            "code": "-2",
                                        }
                                    ],
                                    "text": "AI"
                                },
                                "reason": {
                                    "coding": [
                                        {
                                            "code": 1
                                        }
                                    ],
                                    "text": "rejected"
                                },
                                "value": 1.0
                            }
                        ],
                        "outcome": "complete",
                        "patient": {
                            "reference": "Patient/80DB8910-8D30-4072-B92D-D3F8E74BB17A"
                        },
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
                "use": "claim"
            }
    ]
}