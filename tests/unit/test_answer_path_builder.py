from src.retrieval.answer_path_builder import AnswerPathBuilder
from src.retrieval.routing_contracts import QuestionNeeds, RoutingDecision


def _route(*features):
    return RoutingDecision(
        profile=QuestionNeeds(),
        activated_features=list(features),
    )


def test_condition_root_beats_generic_reference_and_keeps_required_hierarchy():
    result = AnswerPathBuilder().build(
        "Điều kiện để bán tài sản gắn liền với đất thuê là gì?",
        anchors=[{"node_id": "doc_dieu-46_khoan-2_p1", "text": "Bán tài sản thuê trả tiền hằng năm."}],
        explicit_edges=[
            {
                "source_locator": "LD2024:A46:K3",
                "relation_type": "DIRECT_REFERENCE",
                "target_locator": "LD2024:A46:K2",
                "source_text": "Quyền tiếp tục sử dụng đất.",
                "target_text": "Điều kiện chung.",
            },
            {
                "source_locator": "LD2024:A46:K2:Da",
                "relation_type": "REQUIRES_CONDITION_FROM",
                "target_locator": "LD2024:A46:K1",
                "source_text": "Các điều kiện quy định tại khoản 1 Điều này.",
                "target_text": "Điều kiện bán tài sản gắn liền với đất.",
            },
        ],
        descendants=[
            {
                "node_id": "doc_dieu-46_khoan-1_diem-a_p1",
                "parent_locator": "LD2024:A46:K1",
                "text": "Tài sản được tạo lập hợp pháp và đã đăng ký.",
            },
            {
                "node_id": "doc_dieu-46_khoan-1_diem-b_p2",
                "parent_locator": "LD2024:A46:K1",
                "text": "Đã hoàn thành xây dựng theo quy hoạch.",
            },
        ],
        route=_route("requires_reference_traversal"),
    )

    paths = [path["steps"] for path in result.paths]
    assert paths
    assert all(path[0]["source"] == "LD2024:A46:K2:Da" for path in paths)
    assert {path[-1]["target"] for path in paths} == {"LD2024:A46:K1:Da", "LD2024:A46:K1:Db"}


def test_hierarchy_is_not_added_when_no_child_is_relevant_or_a_connector():
    result = AnswerPathBuilder().build(
        "Đối tượng nào được áp dụng?",
        anchors=[{"node_id": "doc_dieu-33_khoan-1_p1", "text": "Quyền của tổ chức kinh tế."}],
        explicit_edges=[
            {
                "source_locator": "LD2024:A41:K1",
                "relation_type": "INHERITS_RIGHTS_OBLIGATIONS",
                "target_locator": "LD2024:A33:K1",
                "source_text": "có quyền và nghĩa vụ theo khoản 1 Điều 33",
                "target_text": "Quyền của tổ chức kinh tế.",
            },
        ],
        descendants=[
            {
                "node_id": "doc_dieu-33_khoan-1_diem-a_p1",
                "parent_locator": "LD2024:A33:K1",
                "text": "Quy định chung về quyền và nghĩa vụ.",
            },
        ],
        route=_route("requires_reference_traversal"),
    )

    assert result.paths == [{"steps": [result.paths[0]["steps"][0]]}]
    assert result.paths[0]["steps"][0]["relation_type"] == "INHERITS_RIGHTS_OBLIGATIONS"


def test_semantic_roles_prefer_matching_subject_and_regime_over_nearby_condition():
    result = AnswerPathBuilder().build(
        "Tổ chức kinh tế thuê đất trả tiền hằng năm muốn bán riêng tài sản trên đất: quy định về quyền bán dẫn đến nhóm điều kiện nào?",
        anchors=[{"node_id": "doc_dieu-46_p1", "text": "Điều kiện bán tài sản gắn liền với đất."}],
        explicit_edges=[
            {
                "source_locator": "LD2024:A34:K1:Dc",
                "relation_type": "REQUIRES_CONDITION_FROM",
                "target_locator": "LD2024:A46",
                "source_text": "Tổ chức kinh tế được Nhà nước cho thuê đất thu tiền thuê đất hằng năm được bán tài sản gắn liền với đất khi đáp ứng Điều 46.",
                "target_text": "Điều kiện bán tài sản gắn liền với đất thuê hằng năm.",
            },
            {
                "source_locator": "LD2024:A46:K5",
                "relation_type": "REQUIRES_CONDITION_FROM",
                "target_locator": "LD2024:A45:K1",
                "source_text": "Dự án xây dựng kinh doanh kết cấu hạ tầng được bán tài sản khi đáp ứng Điều 45.",
                "target_text": "Điều kiện chung của người sử dụng đất.",
            },
        ],
        descendants=[
            {
                "node_id": "doc_dieu-46_khoan-1_p1",
                "parent_locator": "LD2024:A46",
                "text": "Điều kiện bán tài sản gắn liền với đất thuê hằng năm.",
            },
            {
                "node_id": "doc_dieu-46_khoan-1_diem-a_p1",
                "parent_locator": "LD2024:A46:K1",
                "text": "Tài sản được tạo lập hợp pháp và đã đăng ký.",
            },
            {
                "node_id": "doc_dieu-46_khoan-1_diem-b_p2",
                "parent_locator": "LD2024:A46:K1",
                "text": "Đã hoàn thành xây dựng theo quy hoạch.",
            },
        ],
        route=_route("requires_reference_traversal", "requires_multi_hop"),
    )

    assert result.paths
    assert all(path["steps"][0]["source"] == "LD2024:A34:K1:Dc" for path in result.paths)
    assert {path["steps"][-1]["target"] for path in result.paths} == {"LD2024:A46:K1:Da", "LD2024:A46:K1:Db"}


def test_semantic_action_selects_only_the_relevant_right_child():
    result = AnswerPathBuilder().build(
        "Người gốc Việt Nam định cư ở nước ngoài về đầu tư có quyền thế chấp quyền sử dụng đất ở đâu?",
        anchors=[{"node_id": "doc_dieu-41_khoan-1_p1", "text": "Quyền của người gốc Việt Nam đầu tư."}],
        explicit_edges=[
            {
                "source_locator": "LD2024:A41:K1",
                "relation_type": "INHERITS_RIGHTS_OBLIGATIONS",
                "target_locator": "LD2024:A33:K1",
                "source_text": "có quyền và nghĩa vụ quy định tại khoản 1 Điều 33.",
                "target_text": "Quyền của tổ chức kinh tế.",
            },
        ],
        descendants=[
            {
                "node_id": "doc_dieu-33_khoan-1_diem-dd_p1",
                "parent_locator": "LD2024:A33:K1",
                "text": "Thế chấp quyền sử dụng đất tại tổ chức tín dụng.",
            },
            {
                "node_id": "doc_dieu-33_khoan-1_diem-e_p2",
                "parent_locator": "LD2024:A33:K1",
                "text": "Góp vốn bằng quyền sử dụng đất.",
            },
        ],
        route=_route("requires_reference_traversal", "requires_subject_resolution"),
    )

    assert len(result.paths) == 1
    assert result.paths[0]["steps"][-1]["target"] == "LD2024:A33:K1:Dđ"
