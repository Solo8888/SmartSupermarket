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
