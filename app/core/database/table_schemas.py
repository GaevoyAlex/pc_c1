from app.core.security.config import settings

class UsersSchema:
    table_name = settings.DYNAMODB_USERS_TABLE
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'role',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'email-index',
            'KeySchema': [
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'name-index',
            'KeySchema': [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'role-index',
            'KeySchema': [
                {
                    'AttributeName': 'role',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class OTPSchema:
    table_name = settings.DYNAMODB_OTP_TABLE
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'email-index',
            'KeySchema': [
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class TokensSchema:
    table_name = "LiberandumAggregationToken"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'symbol',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'coingecko_id',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'symbol-index',
            'KeySchema': [
                {
                    'AttributeName': 'symbol',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'coingecko-index',
            'KeySchema': [
                {
                    'AttributeName': 'coingecko_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class TokenStatsSchema:
    table_name = "LiberandumAggregationTokenStats"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'symbol',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'coingecko_id',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'symbol-index',
            'KeySchema': [
                {
                    'AttributeName': 'symbol',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'coingecko-index',
            'KeySchema': [
                {
                    'AttributeName': 'coingecko_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class ExchangesSchema:
    table_name = "LiberandumAggregationExchanges"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'name-index',
            'KeySchema': [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class ExchangeStatsSchema:
    table_name = "LiberandumAggregationExchangesStats"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'exchange_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'exchange-id-index',
            'KeySchema': [
                {
                    'AttributeName': 'exchange_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'name-index',
            'KeySchema': [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]



class RoadMapsSchema:
    table_name = "LiberandumApiRoadMaps"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'token_id',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'token-id-index',
            'KeySchema': [
                {
                    'AttributeName': 'token_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class SecurityAuditSchema:
    table_name = "LiberandumApiSecurityAudit"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'title-index',
            'KeySchema': [
                {
                    'AttributeName': 'title',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class PeopleSchema:
    table_name = "LiberandumApiPeople"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'full_name',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'full-name-index',
            'KeySchema': [
                {
                    'AttributeName': 'full_name',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

class PlatformSchema:
    table_name = "LiberandumAggregationTokenPlatform"
    
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'token_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    global_secondary_indexes = [
        {
            'IndexName': 'token-id-index',
            'KeySchema': [
                {
                    'AttributeName': 'token_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'IndexName': 'name-index',
            'KeySchema': [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]

roadmaps_schema = RoadMapsSchema()
security_audit_schema = SecurityAuditSchema()
people_schema = PeopleSchema()
platform_schema = PlatformSchema()
users_schema = UsersSchema()
otp_schema = OTPSchema()
tokens_schema = TokensSchema()
token_stats_schema = TokenStatsSchema()
exchanges_schema = ExchangesSchema()
exchange_stats_schema = ExchangeStatsSchema()