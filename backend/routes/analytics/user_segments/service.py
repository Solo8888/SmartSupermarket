# User segments service
# Provides business logic for user segments API


class UserSegmentsService:
    """用户群体分类服务类"""
    
    def get_user_segments(self):
        """
        获取用户群体分类列表
        
        Returns:
            List[dict]: 用户群体分类列表，每个群体包含segment_id、segment_name、user_count和characteristics字段
        """
        # 模拟用户群体分类数据
        # 在实际环境中，这里应该从数据库或Hadoop系统获取数据
        mock_segments = [
            {
                "segment_id": "1",
                "segment_name": "高价值用户",
                "user_count": 1200,
                "characteristics": ["高消费", "高频购买"]
            },
            {
                "segment_id": "2",
                "segment_name": "价格敏感用户",
                "user_count": 3500,
                "characteristics": ["促销偏好", "低价商品"]
            },
            {
                "segment_id": "3",
                "segment_name": "新用户",
                "user_count": 2800,
                "characteristics": ["注册时间短", "首次购买"]
            },
            {
                "segment_id": "4",
                "segment_name": "流失风险用户",
                "user_count": 1500,
                "characteristics": ["长期未购买", "活跃度低"]
            },
            {
                "segment_id": "5",
                "segment_name": "家庭用户",
                "user_count": 4200,
                "characteristics": ["批量购买", "家庭用品"]
            }
        ]
        
        return mock_segments
    
    def get_user_segment_detail(self, segment_id):
        """
        获取用户群体详情
        
        Args:
            segment_id: 群体ID
            
        Returns:
            dict: 用户群体详情，包含segment_id、segment_name、users、tag_distribution和behavior_analysis字段
            
        Raises:
            ValueError: 当群体ID不存在时
        """
        # 模拟用户群体详情数据
        # 在实际环境中，这里应该从数据库或Hadoop系统获取数据
        mock_segment_details = {
            "1": {
                "segment_id": "1",
                "segment_name": "高价值用户",
                "users": [
                    {"user_id": "1001", "username": "张三", "phone": "13800138001"},
                    {"user_id": "1002", "username": "李四", "phone": "13800138002"},
                    {"user_id": "1003", "username": "王五", "phone": "13800138003"}
                ],
                "tag_distribution": [
                    {"tag_id": "1", "tag_name": "高消费能力", "count": 1000, "percentage": 83.3},
                    {"tag_id": "3", "tag_name": "高频购买", "count": 950, "percentage": 79.2},
                    {"tag_id": "6", "tag_name": "会员活跃", "count": 880, "percentage": 73.3}
                ],
                "behavior_analysis": {
                    "avg_purchase_amount": 588.5,
                    "avg_purchase_frequency": 15.2,
                    "preferred_categories": ["生鲜", "家居", "数码"],
                    "active_time_periods": ["18:00-20:00", "10:00-12:00"]
                }
            },
            "2": {
                "segment_id": "2",
                "segment_name": "价格敏感用户",
                "users": [
                    {"user_id": "2001", "username": "赵六", "phone": "13800138004"},
                    {"user_id": "2002", "username": "孙七", "phone": "13800138005"},
                    {"user_id": "2003", "username": "周八", "phone": "13800138006"}
                ],
                "tag_distribution": [
                    {"tag_id": "4", "tag_name": "价格敏感", "count": 3200, "percentage": 91.4},
                    {"tag_id": "5", "tag_name": "促销偏好", "count": 2800, "percentage": 80.0},
                    {"tag_id": "7", "tag_name": "新品尝鲜", "count": 1500, "percentage": 42.9}
                ],
                "behavior_analysis": {
                    "avg_purchase_amount": 128.3,
                    "avg_purchase_frequency": 8.5,
                    "preferred_categories": ["零食", "日用品", "服装"],
                    "active_time_periods": ["20:00-22:00", "14:00-16:00"]
                }
            },
            "3": {
                "segment_id": "3",
                "segment_name": "新用户",
                "users": [
                    {"user_id": "3001", "username": "吴九", "phone": "13800138007"},
                    {"user_id": "3002", "username": "郑十", "phone": "13800138008"},
                    {"user_id": "3003", "username": "王十一", "phone": "13800138009"}
                ],
                "tag_distribution": [
                    {"tag_id": "7", "tag_name": "新品尝鲜", "count": 2500, "percentage": 89.3},
                    {"tag_id": "5", "tag_name": "促销偏好", "count": 2000, "percentage": 71.4},
                    {"tag_id": "4", "tag_name": "价格敏感", "count": 1800, "percentage": 64.3}
                ],
                "behavior_analysis": {
                    "avg_purchase_amount": 98.7,
                    "avg_purchase_frequency": 2.3,
                    "preferred_categories": ["零食", "饮料", "日用品"],
                    "active_time_periods": ["19:00-21:00", "11:00-13:00"]
                }
            },
            "4": {
                "segment_id": "4",
                "segment_name": "流失风险用户",
                "users": [
                    {"user_id": "4001", "username": "陈十二", "phone": "13800138010"},
                    {"user_id": "4002", "username": "林十三", "phone": "13800138011"},
                    {"user_id": "4003", "username": "黄十四", "phone": "13800138012"}
                ],
                "tag_distribution": [
                    {"tag_id": "4", "tag_name": "价格敏感", "count": 1200, "percentage": 80.0},
                    {"tag_id": "5", "tag_name": "促销偏好", "count": 900, "percentage": 60.0},
                    {"tag_id": "7", "tag_name": "新品尝鲜", "count": 600, "percentage": 40.0}
                ],
                "behavior_analysis": {
                    "avg_purchase_amount": 85.2,
                    "avg_purchase_frequency": 1.1,
                    "preferred_categories": ["日用品", "零食", "饮料"],
                    "active_time_periods": ["21:00-23:00", "15:00-17:00"]
                }
            },
            "5": {
                "segment_id": "5",
                "segment_name": "家庭用户",
                "users": [
                    {"user_id": "5001", "username": "赵十五", "phone": "13800138013"},
                    {"user_id": "5002", "username": "钱十六", "phone": "13800138014"},
                    {"user_id": "5003", "username": "孙十七", "phone": "13800138015"}
                ],
                "tag_distribution": [
                    {"tag_id": "3", "tag_name": "高频购买", "count": 3800, "percentage": 90.5},
                    {"tag_id": "2", "tag_name": "生鲜偏好", "count": 3500, "percentage": 83.3},
                    {"tag_id": "6", "tag_name": "会员活跃", "count": 3200, "percentage": 76.2}
                ],
                "behavior_analysis": {
                    "avg_purchase_amount": 328.6,
                    "avg_purchase_frequency": 12.8,
                    "preferred_categories": ["生鲜", "家居", "日用品"],
                    "active_time_periods": ["09:00-11:00", "17:00-19:00"]
                }
            }
        }
        
        if segment_id not in mock_segment_details:
            raise ValueError(f"群体ID {segment_id} 不存在")
        
        return mock_segment_details[segment_id]
