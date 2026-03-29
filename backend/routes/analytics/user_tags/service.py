# User tags service
# Provides business logic for user tags API


class UserTagsService:
    """用户标签服务类"""
    
    def get_user_tags(self):
        """
        获取用户标签列表
        
        Returns:
            List[dict]: 用户标签列表，每个标签包含tag_id、tag_name和weight字段
        """
        # 模拟用户标签数据
        # 在实际环境中，这里应该从数据库或Hadoop系统获取数据
        mock_tags = [
            {"tag_id": "1", "tag_name": "高消费能力", "weight": 0.9},
            {"tag_id": "2", "tag_name": "生鲜偏好", "weight": 0.75},
            {"tag_id": "3", "tag_name": "高频购买", "weight": 0.8},
            {"tag_id": "4", "tag_name": "价格敏感", "weight": 0.6},
            {"tag_id": "5", "tag_name": "促销偏好", "weight": 0.7},
            {"tag_id": "6", "tag_name": "会员活跃", "weight": 0.85},
            {"tag_id": "7", "tag_name": "新品尝鲜", "weight": 0.65},
            {"tag_id": "8", "tag_name": "家庭购买", "weight": 0.72}
        ]
        
        return mock_tags
