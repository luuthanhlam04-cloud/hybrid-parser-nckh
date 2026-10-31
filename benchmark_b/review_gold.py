"""Create an AI-assisted gold audit candidate without claiming human review."""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from .prepare import MAP, V2, sha


OUTPUT = Path("datasets/benchmarks/benchmark_B_v03_ai_reviewed.json")
SIGNOFF_CSV = Path("datasets/benchmarks/benchmark_B_v03_human_signoff.csv")
STATUS = "AI_ASSISTED_VERIFIED_PENDING_HUMAN_SIGNOFF"

# Human-review round 1 rejected these questions.  The revisions below are
# applied to the reproducible candidate source; approved questions are left
# untouched.  Negative questions keep context anchors separate from scored
# gold evidence so an out-of-corpus answer cannot receive retrieval credit.
ROUND1_REVISED_IDS = {
    "B002", "B009", "B011", "B012", "B013", "B015", "B017", "B018",
    "B028", "B032", "B034", "B036", "B040", "B041", "B048", "B049", "B050",
}

# Round 2 approved 15/17 revised questions.  Only these two are changed again
# and therefore returned to PENDING for a focused third review.
REVISED_QUESTION_IDS = {"B009", "B011"}

ARTICLE_46_BUILD_EXCEPTION = (
    "Ngoại lệ đối với yêu cầu hoàn thành xây dựng: trường hợp phải thực hiện theo bản án, "
    "quyết định của Tòa án đã có hiệu lực thi hành; quyết định cưỡng chế của cơ quan thi "
    "hành án dân sự; hoặc kết luận của cơ quan nhà nước có thẩm quyền về thanh tra, kiểm tra."
)

QUESTION_REVISIONS = {
    "B002": {
        "question": "Theo điểm c khoản 3 Điều 27, việc công chứng hoặc chứng thực văn bản về thừa kế quyền sử dụng đất được thực hiện theo hệ thống pháp luật nào?",
        "facts": [("Việc công chứng hoặc chứng thực văn bản về thừa kế quyền sử dụng đất được thực hiện theo quy định của pháp luật về dân sự.", ["LD2024:A27:K3:Dc"])],
        "answer": "Theo điểm c khoản 3 Điều 27, việc công chứng hoặc chứng thực văn bản về thừa kế quyền sử dụng đất được thực hiện theo quy định của pháp luật về dân sự. Quy định này không tự nó khẳng định mọi văn bản thừa kế đều bắt buộc phải công chứng.",
        "forbidden": ["Khẳng định mọi văn bản về thừa kế quyền sử dụng đất đều bắt buộc phải công chứng chỉ dựa vào điểm c khoản 3 Điều 27."],
    },
    "B009": {
        "facts": [
            ("Đối với chuyển nhượng quyền sử dụng đất, phải có một trong các loại giấy chứng nhận được điểm a khoản 1 Điều 45 liệt kê, trừ trường hợp tổ chức kinh tế có vốn đầu tư nước ngoài nhận chuyển nhượng dự án bất động sản theo khoản 7 Điều 124 hoặc trường hợp hộ gia đình, cá nhân đủ điều kiện cấp giấy nhưng chưa được cấp giấy thực hiện chuyển nhượng để làm dự án theo điểm a khoản 4 Điều 127.", ["LD2024:A45:K1:Da"]),
            ("Đất không có tranh chấp hoặc tranh chấp đã được giải quyết bằng quyết định, bản án hoặc phán quyết có hiệu lực.", ["LD2024:A45:K1:Db"]),
            ("Quyền sử dụng đất không bị kê biên hoặc áp dụng biện pháp khác để bảo đảm thi hành án.", ["LD2024:A45:K1:Dc"]),
            ("Đất đang trong thời hạn sử dụng.", ["LD2024:A45:K1:Dd"]),
            ("Quyền sử dụng đất không bị áp dụng biện pháp khẩn cấp tạm thời.", ["LD2024:A45:K1:Dđ"]),
        ],
        "exceptions": ["Riêng đối với giao dịch chuyển nhượng được hỏi, ngoại lệ về giấy chứng nhận gồm trường hợp tổ chức kinh tế có vốn đầu tư nước ngoài nhận chuyển nhượng dự án bất động sản theo khoản 7 Điều 124 và trường hợp hộ gia đình, cá nhân đủ điều kiện cấp giấy nhưng chưa được cấp giấy thực hiện chuyển nhượng để làm dự án theo điểm a khoản 4 Điều 127. Các ngoại lệ về thừa kế, chuyển đổi đất nông nghiệp khi dồn điền đổi thửa và tặng cho Nhà nước hoặc cộng đồng dân cư là các loại giao dịch khác."],
        "exception_support": [["LD2024:A45:K1:Da"]],
        "answer": "Đối với chuyển nhượng quyền sử dụng đất, người sử dụng đất phải có Giấy chứng nhận quyền sử dụng đất; Giấy chứng nhận quyền sở hữu nhà ở và quyền sử dụng đất ở; Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất; hoặc Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất. Ngoại lệ liên quan đến chuyển nhượng gồm: tổ chức kinh tế có vốn đầu tư nước ngoài nhận chuyển nhượng dự án bất động sản theo khoản 7 Điều 124; và hộ gia đình, cá nhân đủ điều kiện cấp giấy nhưng chưa được cấp giấy thực hiện chuyển nhượng để làm dự án theo điểm a khoản 4 Điều 127. Các ngoại lệ về thừa kế, chuyển đổi đất nông nghiệp khi dồn điền đổi thửa và tặng cho Nhà nước hoặc cộng đồng dân cư là các loại giao dịch khác. Ngoài ra, đất không có tranh chấp hoặc tranh chấp đã được giải quyết bằng quyết định, bản án hoặc phán quyết có hiệu lực; quyền sử dụng đất không bị kê biên hoặc áp dụng biện pháp khác để bảo đảm thi hành án; đất còn thời hạn sử dụng; và quyền sử dụng đất không bị áp dụng biện pháp khẩn cấp tạm thời.",
        "retrieval_evidence_set": ["LD2024:A45:K1:Da", "LD2024:A45:K1:Db", "LD2024:A45:K1:Dc", "LD2024:A45:K1:Dd", "LD2024:A45:K1:Dđ"],
    },
    "B011": {
        "question": "Tổ chức kinh tế, cá nhân, người gốc Việt Nam định cư ở nước ngoài hoặc tổ chức kinh tế có vốn đầu tư nước ngoài muốn bán riêng tài sản gắn liền với đất được Nhà nước cho thuê thu tiền hằng năm phải đáp ứng những điều kiện nào?",
        "answer": "Tài sản gắn liền với đất thuê phải được tạo lập hợp pháp và đã đăng ký theo pháp luật; đồng thời việc xây dựng phải hoàn thành đúng quy hoạch xây dựng chi tiết và dự án đầu tư đã được phê duyệt, chấp thuận nếu có. Ngoại lệ của yêu cầu hoàn thành xây dựng là trường hợp phải thực hiện theo bản án, quyết định của Tòa án đã có hiệu lực thi hành, quyết định cưỡng chế của cơ quan thi hành án dân sự hoặc kết luận thanh tra, kiểm tra của cơ quan nhà nước có thẩm quyền.",
        "exceptions": [ARTICLE_46_BUILD_EXCEPTION],
        "exception_support": [["LD2024:A46:K1:Db"]],
    },
    "B012": {
        "facts": [
            ("Phải đáp ứng toàn bộ điều kiện bán tài sản gắn liền với đất tại khoản 1 Điều 46.", ["LD2024:A46:K2:Da"]),
            ("Tài sản gắn liền với đất thuê được tạo lập hợp pháp và đã đăng ký theo pháp luật.", ["LD2024:A46:K1:Da"]),
            ("Việc xây dựng đã hoàn thành đúng quy hoạch xây dựng chi tiết và dự án đầu tư được phê duyệt, chấp thuận nếu có, trừ ba nhóm ngoại lệ tại điểm b khoản 1 Điều 46.", ["LD2024:A46:K1:Db"]),
            ("Đã ứng trước tiền bồi thường, hỗ trợ, tái định cư mà chưa khấu trừ hết vào tiền thuê đất phải nộp.", ["LD2024:A46:K2:Db"]),
        ],
        "exceptions": [ARTICLE_46_BUILD_EXCEPTION],
        "exception_support": [["LD2024:A46:K1:Db"]],
        "answer": "Bên thuê phải đáp ứng toàn bộ điều kiện tại khoản 1 Điều 46: tài sản được tạo lập hợp pháp, đã đăng ký; việc xây dựng đã hoàn thành đúng quy hoạch xây dựng chi tiết và dự án đầu tư được phê duyệt, chấp thuận nếu có. Ngoại lệ của yêu cầu hoàn thành xây dựng gồm trường hợp thực hiện theo bản án hoặc quyết định Tòa án có hiệu lực, quyết định cưỡng chế thi hành án dân sự, hoặc kết luận thanh tra, kiểm tra của cơ quan có thẩm quyền. Ngoài ra, bên thuê phải đã ứng trước tiền bồi thường, hỗ trợ, tái định cư mà chưa khấu trừ hết vào tiền thuê đất phải nộp.",
        "retrieval_evidence_set": ["LD2024:A46:K2:Da", "LD2024:A46:K2:Db", "LD2024:A46:K1:Da", "LD2024:A46:K1:Db"],
    },
    "B013": {
        "facts": [
            ("Theo nguyên tắc tại điểm a khoản 3 Điều 27, hợp đồng chuyển nhượng, tặng cho, thế chấp, góp vốn bằng quyền sử dụng đất hoặc bằng quyền sử dụng đất và tài sản gắn liền với đất phải được công chứng hoặc chứng thực.", ["LD2024:A27:K3:Da"]),
            ("Hợp đồng cho thuê, cho thuê lại quyền sử dụng đất hoặc quyền sử dụng đất và tài sản gắn liền với đất, cùng hợp đồng chuyển đổi quyền sử dụng đất nông nghiệp, được công chứng hoặc chứng thực theo yêu cầu của các bên.", ["LD2024:A27:K3:Db"]),
            ("Hợp đồng chuyển nhượng hoặc góp vốn bằng quyền sử dụng đất, quyền sử dụng đất và tài sản gắn liền với đất, hoặc tài sản gắn liền với đất mà một bên hoặc các bên là tổ chức hoạt động kinh doanh bất động sản được công chứng hoặc chứng thực theo yêu cầu của các bên.", ["LD2024:A27:K3:Db"]),
        ],
        "exceptions": ["Các giao dịch được liệt kê tại điểm b khoản 3 Điều 27 là ngoại lệ đối với nguyên tắc bắt buộc tại điểm a và được công chứng hoặc chứng thực theo yêu cầu của các bên."],
        "exception_support": [["LD2024:A27:K3:Da", "LD2024:A27:K3:Db"]],
        "answer": "Theo nguyên tắc, hợp đồng chuyển nhượng, tặng cho, thế chấp, góp vốn bằng quyền sử dụng đất hoặc bằng quyền sử dụng đất và tài sản gắn liền với đất phải được công chứng hoặc chứng thực. Theo yêu cầu của các bên áp dụng đối với: hợp đồng cho thuê, cho thuê lại quyền sử dụng đất hoặc quyền sử dụng đất và tài sản gắn liền với đất; hợp đồng chuyển đổi quyền sử dụng đất nông nghiệp; và hợp đồng chuyển nhượng, góp vốn bằng quyền sử dụng đất, quyền sử dụng đất và tài sản gắn liền với đất, hoặc tài sản gắn liền với đất mà một bên hoặc các bên là tổ chức hoạt động kinh doanh bất động sản.",
    },
    "B015": {
        "question": "Tổ chức trong nước được giao đất có thu tiền hoặc thuê đất trả tiền một lần để thực hiện dự án đầu tư có mục đích kinh doanh mà được miễn, giảm tiền sử dụng đất hoặc tiền thuê đất thì quyền chuyển nhượng, góp vốn và khoản tiền phải nộp được xác định ra sao?",
        "answer": "Tổ chức có quyền và nghĩa vụ như trường hợp không được miễn hoặc giảm tiền sử dụng đất, tiền thuê đất. Khi chuyển nhượng hoặc góp vốn bằng quyền sử dụng đất, tổ chức phải nộp cho Nhà nước khoản tiền tương ứng với số tiền sử dụng đất hoặc tiền thuê đất đã được miễn, giảm tại thời điểm giao đất, cho thuê đất hoặc cho phép chuyển mục đích sử dụng đất, trừ trường hợp pháp luật có liên quan có quy định khác.",
        "exceptions": ["Không áp dụng yêu cầu nộp khoản tiền tương ứng nếu pháp luật có liên quan có quy định khác."],
        "exception_support": [["LD2024:A33:K3:Db"]],
    },
    "B017": {
        "question": "Nếu tất cả người nhận thừa kế đều là người nước ngoài hoặc người gốc Việt Nam định cư ở nước ngoài không thuộc đối tượng được sở hữu nhà ở gắn liền với quyền sử dụng đất ở tại Việt Nam, họ được xử lý quyền sử dụng đất thừa kế bằng những cách nào?",
        "facts": [
            ("Những người nhận thừa kế này không được cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất.", ["LD2024:A44:K3"]),
            ("Họ được chuyển nhượng quyền sử dụng đất thừa kế và chính người nhận thừa kế đứng tên bên chuyển nhượng.", ["LD2024:A44:K3:Da"]),
            ("Họ được tặng cho quyền sử dụng đất nếu người nhận tặng cho thuộc đối tượng tại điểm e khoản 1 Điều 37 và phù hợp pháp luật về nhà ở; người nhận thừa kế đứng tên bên tặng cho.", ["LD2024:A44:K3:Db", "LD2024:A37:K1:De"]),
            ("Nếu chưa chuyển nhượng hoặc tặng cho, người nhận thừa kế hoặc người đại diện được ủy quyền bằng văn bản nộp hồ sơ nhận thừa kế tại tổ chức đăng ký đất đai để cập nhật Sổ địa chính.", ["LD2024:A44:K3:Dc"]),
        ],
        "answer": "Họ không được cấp Giấy chứng nhận nhưng được chuyển nhượng quyền sử dụng đất thừa kế và đứng tên bên chuyển nhượng. Họ cũng có thể tặng cho quyền sử dụng đất nếu người nhận tặng cho thuộc đối tượng tại điểm e khoản 1 Điều 37 và phù hợp pháp luật về nhà ở; người nhận thừa kế đứng tên bên tặng cho. Nếu chưa chuyển nhượng hoặc tặng cho, người nhận thừa kế hoặc người đại diện được ủy quyền bằng văn bản phải nộp hồ sơ tại tổ chức đăng ký đất đai để cập nhật Sổ địa chính.",
    },
    "B018": {
        "question": "Cá nhân thuê lại đất trong khu công nghiệp được áp dụng quyền và nghĩa vụ theo khoản nào của Điều 37 khi trả tiền một lần và khi trả tiền hằng năm?",
        "answer": "Nếu trả tiền thuê đất hoặc thuê lại đất một lần cho cả thời gian thuê thì áp dụng quyền và nghĩa vụ tại khoản 1 Điều 37. Nếu trả tiền thuê đất hoặc thuê lại đất hằng năm thì áp dụng quyền và nghĩa vụ tại khoản 2 Điều 37.",
    },
    "B028": {
        "answer": "Điểm c khoản 1 Điều 34 cho phép bán tài sản gắn liền với đất khi đáp ứng Điều 46. Đối với bán riêng tài sản, khoản 1 Điều 46 yêu cầu tài sản được tạo lập hợp pháp và đã đăng ký; việc xây dựng hoàn thành đúng quy hoạch xây dựng chi tiết và dự án đầu tư được phê duyệt, chấp thuận nếu có. Ngoại lệ của yêu cầu hoàn thành xây dựng gồm trường hợp thực hiện theo bản án hoặc quyết định Tòa án có hiệu lực, quyết định cưỡng chế thi hành án dân sự, hoặc kết luận thanh tra, kiểm tra của cơ quan có thẩm quyền.",
        "exceptions": [ARTICLE_46_BUILD_EXCEPTION],
        "exception_support": [["LD2024:A46:K1:Db"]],
    },
    "B032": {
        "facts": [
            ("Điểm b khoản 2 Điều 38 dẫn tới quyền và nghĩa vụ tại khoản 2 Điều 37.", ["LD2024:A38:K2:Db"]),
            ("Điểm a khoản 2 Điều 37 dẫn tới nghĩa vụ chung, trong đó khoản 3 Điều 31 yêu cầu thực hiện nghĩa vụ tài chính về đất đai.", ["LD2024:A37:K2:Da", "LD2024:A31:K3"]),
            ("Điểm b khoản 2 Điều 37 cho phép bán tài sản gắn liền với đất khi đáp ứng Điều 46.", ["LD2024:A37:K2:Db"]),
            ("Khoản 1 Điều 46 yêu cầu tài sản được tạo lập hợp pháp, đã đăng ký và hoàn thành xây dựng đúng quy hoạch, dự án, trừ ba nhóm ngoại lệ tại điểm b.", ["LD2024:A46:K1:Da", "LD2024:A46:K1:Db"]),
        ],
        "exceptions": [ARTICLE_46_BUILD_EXCEPTION],
        "exception_support": [["LD2024:A46:K1:Db"]],
        "answer": "Điểm b khoản 2 Điều 38 dẫn tới khoản 2 Điều 37. Theo điểm a khoản 2 Điều 37 và khoản 3 Điều 31, cá nhân phải thực hiện nghĩa vụ tài chính về đất đai. Điểm b khoản 2 Điều 37 cho phép bán tài sản gắn liền với đất khi đáp ứng Điều 46: tài sản phải được tạo lập hợp pháp, đã đăng ký và hoàn thành xây dựng đúng quy hoạch, dự án. Ngoại lệ của yêu cầu hoàn thành xây dựng gồm trường hợp thực hiện theo bản án hoặc quyết định Tòa án có hiệu lực, quyết định cưỡng chế thi hành án dân sự, hoặc kết luận thanh tra, kiểm tra của cơ quan có thẩm quyền.",
        "retrieval_evidence_set": ["LD2024:A38:K2:Db", "LD2024:A37:K2:Db", "LD2024:A31:K3", "LD2024:A46:K1:Da", "LD2024:A46:K1:Db"],
    },
    "B034": {
        "answer": "Điểm b khoản 2 Điều 43 dẫn tới khoản 1 Điều 34; điểm c khoản 1 Điều 34 cho phép bán tài sản gắn liền với đất khi đáp ứng Điều 46. Điểm a khoản 1 Điều 46 yêu cầu tài sản được tạo lập hợp pháp và đã đăng ký. Điểm b yêu cầu hoàn thành xây dựng đúng quy hoạch, dự án; ngoại lệ gồm trường hợp thực hiện theo bản án hoặc quyết định Tòa án có hiệu lực, quyết định cưỡng chế thi hành án dân sự, hoặc kết luận thanh tra, kiểm tra của cơ quan có thẩm quyền.",
        "exceptions": [ARTICLE_46_BUILD_EXCEPTION],
        "exception_support": [["LD2024:A46:K1:Db"]],
        "retrieval_evidence_set": ["LD2024:A43:K2:Db", "LD2024:A34:K1:Dc", "LD2024:A46:K1:Da", "LD2024:A46:K1:Db"],
    },
    "B036": {
        "facts": [
            ("Không: cá nhân thuê đất trả tiền hằng năm chỉ được thế chấp tài sản thuộc sở hữu của mình gắn liền với đất theo điểm đ khoản 2 Điều 37, không phải quyền sử dụng đất.", ["LD2024:A37:K2:Dđ"]),
            ("Quyền thế chấp cả quyền sử dụng đất và tài sản gắn liền với đất tại điểm g khoản 1 Điều 37 chỉ áp dụng cho các hình thức sử dụng đất được khoản 1 liệt kê.", ["LD2024:A37:K1:Dg"]),
        ],
        "answer": "Không. Cá nhân thuê đất của Nhà nước trả tiền hằng năm chỉ được thế chấp tài sản thuộc sở hữu của mình gắn liền với đất theo điểm đ khoản 2 Điều 37, không được thế chấp quyền sử dụng đất theo quy định này. Quyền thế chấp cả quyền sử dụng đất và tài sản tại điểm g khoản 1 chỉ áp dụng cho các hình thức sử dụng đất được khoản 1 liệt kê.",
    },
    "B040": {
        "question": "Khi hợp tác xã hoặc liên hiệp hợp tác xã giải thể, phá sản, những nhóm đất nào bị Nhà nước thu hồi và những nhóm đất nào không bị thu hồi theo khoản 2 Điều 36?",
        "facts": [
            ("Đất được Nhà nước giao không thu tiền sử dụng đất thuộc nhóm bị Nhà nước thu hồi.", ["LD2024:A36:K2:Da"]),
            ("Đất được giao có thu tiền, đất thuê, đất do mua tài sản gắn liền với đất hoặc nhận chuyển nhượng hợp pháp mà các khoản tiền tương ứng có nguồn gốc Nhà nước hỗ trợ thuộc nhóm bị thu hồi.", ["LD2024:A36:K2:Da"]),
            ("Các nguồn đất được điểm b khoản 2 Điều 36 liệt kê mà khoản tiền tương ứng không có nguồn gốc Nhà nước hỗ trợ, cùng đất do thành viên góp quyền sử dụng, không bị thu hồi; quyền sử dụng đất thuộc hợp tác xã, liên hiệp hợp tác xã và được xử lý theo điều lệ, nghị quyết đại hội thành viên.", ["LD2024:A36:K2:Db"]),
        ],
        "answer": "Nhà nước thu hồi đất được giao không thu tiền sử dụng đất. Nhà nước cũng thu hồi các nhóm đất được giao có thu tiền, cho thuê, do mua tài sản gắn liền với đất hoặc nhận chuyển nhượng hợp pháp nếu tiền sử dụng đất, tiền thuê đất, tiền mua tài sản hoặc tiền nhận chuyển nhượng có nguồn gốc Nhà nước hỗ trợ. Đối với các nguồn đất được điểm b khoản 2 Điều 36 liệt kê mà khoản tiền tương ứng không có nguồn gốc Nhà nước hỗ trợ, và đất do thành viên góp quyền sử dụng, Nhà nước không thu hồi; quyền sử dụng đất thuộc hợp tác xã, liên hiệp hợp tác xã và được xử lý theo điều lệ, nghị quyết đại hội thành viên.",
    },
    "B041": {
        "facts": [
            ("Được chuyển nhượng quyền sử dụng đất và tài sản thuộc sở hữu của mình gắn liền với đất.", ["LD2024:A33:K1:Db"]),
            ("Đối với trường hợp được Nhà nước giao đất có thu tiền sử dụng đất, được cho thuê quyền sử dụng đất và tài sản thuộc sở hữu của mình gắn liền với đất; quyền cho thuê lại tại điểm c dành cho trường hợp được Nhà nước cho thuê đất trả tiền một lần.", ["LD2024:A33:K1:Dc"]),
            ("Được tặng cho quyền sử dụng đất trong các trường hợp, mục đích công ích được luật liệt kê.", ["LD2024:A33:K1:Dd"]),
            ("Được thế chấp quyền sử dụng đất và tài sản gắn liền với đất tại các chủ thể luật cho phép.", ["LD2024:A33:K1:Dđ"]),
            ("Được góp vốn bằng quyền sử dụng đất và tài sản gắn liền với đất với các chủ thể luật cho phép.", ["LD2024:A33:K1:De"]),
        ],
        "answer": "Tổ chức kinh tế được giao đất có thu tiền được chuyển nhượng quyền sử dụng đất và tài sản gắn liền với đất; cho thuê quyền sử dụng đất và tài sản gắn liền với đất; tặng cho trong các trường hợp luật liệt kê; thế chấp; và góp vốn bằng quyền sử dụng đất, tài sản gắn liền với đất. Không được suy rộng rằng trường hợp được giao đất có thu tiền mặc nhiên có quyền cho thuê lại; quyền cho thuê lại tại điểm c áp dụng cho trường hợp được Nhà nước cho thuê đất trả tiền một lần cho cả thời gian thuê.",
        "forbidden": ["Khẳng định tổ chức kinh tế được giao đất có thu tiền mặc nhiên có quyền cho thuê lại quyền sử dụng đất."],
        "retrieval_evidence_set": ["LD2024:A33:K1:Db", "LD2024:A33:K1:Dc", "LD2024:A33:K1:Dd", "LD2024:A33:K1:Dđ", "LD2024:A33:K1:De"],
    },
    "B048": {
        "gold_locators": [],
        "supporting_anchor_locators": ["LD2024:A27:K1"],
        "fact_evidence_empty": True,
        "annotation_note": "Điều 27 khoản 1 chỉ là context anchor về quyền chuyển nhượng; Chương III không cung cấp thuế suất và Điều 47 không được dùng làm gold evidence cho câu hỏi này.",
    },
    "B049": {
        "gold_locators": [],
        "supporting_anchor_locators": ["LD2024:A29:K2"],
        "fact_evidence_empty": True,
        "annotation_note": "Điều 29 khoản 2 là context anchor dẫn tới Điều 133 ngoài corpus, không phải gold evidence về số ngày giải quyết.",
    },
    "B050": {
        "gold_locators": [],
        "supporting_anchor_locators": ["LD2024:A48:K1"],
        "fact_evidence_empty": True,
        "facts": [
            ("Khoản 1 Điều 48 chỉ là context anchor dẫn chiếu khoản 2 và khoản 3 Điều 16 về đối tượng liên quan.", []),
            ("Chương III không cung cấp chính xác tiêu chí hộ nghèo, thu nhập và địa bàn; phải tra cứu Điều 16 và quy định liên quan.", []),
        ],
        "answer": "Không. Chương III không cung cấp chính xác tiêu chí hộ nghèo, thu nhập và địa bàn. Khoản 1 Điều 48 chỉ dẫn chiếu tới khoản 2 và khoản 3 Điều 16; vì vậy phải tra cứu Điều 16 và quy định liên quan, không được suy đoán tiêu chí.",
    },
}

# The first three were direct/conditional questions incorrectly tagged multi-hop.
CATEGORY_OVERRIDES = {"B041": "single_hop", "B042": "single_hop", "B043": "conditional"}

# Legal semantics for non-structural reference edges reviewed against Chapter III.
EDGE_TYPE_OVERRIDES = {
    ("LD2024:A46:K2:Da", "LD2024:A46:K1"): "REQUIRES_CONDITION_FROM",
    ("LD2024:A27:K3:Da", "LD2024:A27:K3:Db"): "EXCEPTION_REFERENCE",
    ("LD2024:A36:K1", "LD2024:A33"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A37:K3:Da", "LD2024:A37:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A37:K3:Db", "LD2024:A37:K2"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A34:K2", "LD2024:A34:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A48:K3", "LD2024:A48:K1"): "EXCEPTION_REFERENCE",
    ("LD2024:A48:K3", "LD2024:A48:K2"): "EXCEPTION_REFERENCE",
    ("LD2024:A33:K2", "LD2024:A33:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A34:K1:Dc", "LD2024:A46"): "REQUIRES_CONDITION_FROM",
    ("LD2024:A35:K3:Dc", "LD2024:A34:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A41:K1", "LD2024:A33:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A45:K3:Db", "LD2024:A47"): "REQUIRES_CONDITION_FROM",
    ("LD2024:A38:K2:Db", "LD2024:A37:K2"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A37:K2:Da", "LD2024:A31"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A37:K2:Db", "LD2024:A46"): "REQUIRES_CONDITION_FROM",
    ("LD2024:A42:K2:Da", "LD2024:A41:K2"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A41:K2:Da", "LD2024:A31"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A43:K2:Db", "LD2024:A34:K1"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A45:K7", "LD2024:A45:K6"): "REQUIRES_CONDITION_FROM",
    ("LD2024:A42:K2:Db", "LD2024:A41:K3"): "INHERITS_RIGHTS_OBLIGATIONS",
    ("LD2024:A42:K2:Dc", "LD2024:A41:K3"): "INHERITS_RIGHTS_OBLIGATIONS",
}

# Facts not listed here retain REQUIRED_FACT. Roles only drive metric applicability.
CONDITION_FACTS = {
    *(f"B009_F{i:02d}" for i in range(1, 6)),
    *(f"B010_F{i:02d}" for i in range(1, 7)),
    *(f"B011_F{i:02d}" for i in range(1, 4)),
    *(f"B012_F{i:02d}" for i in range(1, 5)),
    *(f"B014_F{i:02d}" for i in range(1, 5)),
    "B015_F02", "B016_F01", "B016_F02", "B021_F01", "B021_F02",
    "B022_F01", "B023_F01", "B024_F01", "B024_F02", "B025_F01",
    "B028_F02", "B031_F02", "B032_F04", "B034_F03", "B034_F04",
    "B035_F01", "B035_F02", "B035_F03", "B043_F01", "B043_F02",
    "B043_F03", "B045_F01", "B045_F02",
}
SUBJECT_FACTS = {
    "B003_F01", "B005_F01", "B007_F01", "B016_F03", "B018_F01",
    "B018_F02", "B019_F01", "B020_F01", "B020_F02", "B023_F02",
    "B025_F02", "B025_F03", "B027_F02", "B029_F02", "B033_F01",
    "B036_F01", "B036_F02", "B037_F01", "B037_F02", "B038_F01",
    "B038_F02", "B038_F03", "B038_F04", "B040_F01", "B040_F02", "B040_F03",
    "B042_F01", "B042_F02", "B042_F03", "B042_F04", "B047_F01",
    "B047_F02",
}


def _apply_human_review_revision(question: dict) -> None:
    revision = QUESTION_REVISIONS.get(question["question_id"])
    if not revision:
        return

    for source_key, target_key in (
        ("question", "question"),
        ("answer", "reference_answer"),
        ("annotation_note", "annotation_note"),
    ):
        if source_key in revision:
            question[target_key] = revision[source_key]

    if "gold_locators" in revision:
        wanted = set(revision["gold_locators"])
        question["gold_locations"] = [
            location for location in question["gold_locations"]
            if location["canonical_locator"] in wanted
        ]
    question["supporting_anchor_locators"] = revision.get(
        "supporting_anchor_locators", question.get("supporting_anchor_locators", [])
    )

    if "facts" in revision:
        required_facts = []
        detailed = []
        annotations = []
        for index, (fact_text, evidence) in enumerate(revision["facts"], start=1):
            fact_id = f"{question['question_id']}_F{index:02d}"
            required_facts.append(fact_text)
            detailed.append({
                "fact_id": fact_id,
                "fact": fact_text,
                "evidence_locators": evidence,
                "source_status": (
                    "SCOPE_ASSESSMENT" if question["answerability"] == "INSUFFICIENT_CORPUS"
                    else "SUPPORTED_BY_CHAPTER_III"
                ),
            })
            annotations.append({
                "fact_id": fact_id,
                "text": fact_text,
                "role": "UNREVIEWED",
                "required": True,
                "weight": 1,
                "evidence_any_of": evidence,
                "review_status": "HUMAN_REVIEW_REQUIRED",
            })
        question["required_atomic_facts"] = required_facts
        question["atomic_facts_detailed"] = detailed
        question["atomic_annotations"] = annotations

    if revision.get("fact_evidence_empty"):
        for fact in question.get("atomic_facts_detailed", []):
            fact["evidence_locators"] = []
            fact["source_status"] = "SCOPE_ASSESSMENT"
        for fact in question.get("atomic_annotations", []):
            fact["evidence_any_of"] = []

    if "exceptions" in revision:
        question["required_exceptions"] = revision["exceptions"]
    if "forbidden" in revision:
        question["forbidden_claims"] = revision["forbidden"]

    gold_locators = [location["canonical_locator"] for location in question["gold_locations"]]
    exception_support = revision.get("exception_support", [])
    question["required_exceptions_annotations"] = [
        {
            "annotation_id": f"{question['question_id']}_EXCEPTION_{index}",
            "text": text,
            "role": "EXCEPTION",
            "supporting_locators": exception_support[index - 1] if index <= len(exception_support) else gold_locators,
            "candidate_locators": exception_support[index - 1] if index <= len(exception_support) else gold_locators,
            "review_status": "HUMAN_REVIEW_REQUIRED",
        }
        for index, text in enumerate(question.get("required_exceptions", []), start=1)
    ]
    question["forbidden_claims_annotations"] = [
        {
            "annotation_id": f"{question['question_id']}_FORBIDDEN_CLAIM_{index}",
            "text": text,
            "role": "FORBIDDEN_CLAIM",
            "supporting_locators": gold_locators,
            "candidate_locators": gold_locators,
            "review_status": "HUMAN_REVIEW_REQUIRED",
        }
        for index, text in enumerate(question.get("forbidden_claims", []), start=1)
    ]

    retrieval_locators = revision.get("retrieval_evidence_set")
    if retrieval_locators is not None:
        question["acceptable_evidence_sets"] = [retrieval_locators]
        question["hierarchy_requirements"] = {
            "parent_context": [locator for locator in retrieval_locators if ":D" not in locator],
            "child_evidence": [locator for locator in retrieval_locators if ":D" in locator],
        }
    elif not question["gold_locations"]:
        question["acceptable_evidence_sets"] = []
        question["hierarchy_requirements"] = {"parent_context": [], "child_evidence": []}


def build() -> dict:
    source = json.loads(V2.read_text(encoding="utf-8"))
    payload = copy.deepcopy(source)
    mapping = json.loads(MAP.read_text(encoding="utf-8"))["mappings"]
    all_locators: set[str] = set()
    edge_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}

    prior_signoff: dict[str, dict[str, str]] = {}
    if SIGNOFF_CSV.exists():
        with SIGNOFF_CSV.open(encoding="utf-8-sig", newline="") as stream:
            prior_signoff = {row["question_id"]: row for row in csv.DictReader(stream)}

    for question in payload["questions"]:
        qid = question["question_id"]
        _apply_human_review_revision(question)
        question["category"] = CATEGORY_OVERRIDES.get(qid, question["category"])
        if qid == "B022":
            precise = (
                "Cá nhân không sinh sống trong khu vực rừng phòng hộ, rừng đặc dụng không được nhận "
                "chuyển nhượng hoặc nhận tặng cho đất ở và đất khác trong khu vực rừng phòng hộ, "
                "phân khu bảo vệ nghiêm ngặt hoặc phân khu phục hồi sinh thái thuộc rừng đặc dụng."
            )
            question["reference_answer"] = precise
            question["required_atomic_facts"] = [precise]
            question["atomic_facts_detailed"][0]["fact"] = precise
            question["atomic_annotations"][0]["text"] = precise

        for location in question["gold_locations"]:
            locator = location["canonical_locator"]
            all_locators.add(locator)
            if locator not in mapping:
                raise ValueError(f"{qid}: unmapped gold locator {locator}")
            if location.get("node_id") != mapping[locator]["physical_node_id"]:
                raise ValueError(f"{qid}: physical ID mismatch for {locator}")

        for locator in question.get("supporting_anchor_locators", []):
            if locator not in mapping:
                raise ValueError(f"{qid}: unmapped supporting anchor {locator}")

        for fact in question.get("atomic_annotations", []):
            fid = fact["fact_id"]
            fact["role"] = (
                "SUBJECT_SCOPE" if fid in SUBJECT_FACTS else
                "REQUIRED_CONDITION" if fid in CONDITION_FACTS else
                "REQUIRED_FACT"
            )
            fact["review_status"] = STATUS
            role_counts[fact["role"]] = role_counts.get(fact["role"], 0) + 1
            if not fact.get("evidence_any_of"):
                if question["answerability"] != "INSUFFICIENT_CORPUS":
                    raise ValueError(f"{qid}/{fid}: missing evidence locator")
            for locator in fact["evidence_any_of"]:
                if locator not in mapping:
                    raise ValueError(f"{qid}/{fid}: unmapped fact locator {locator}")

        for annotation in question.get("required_exceptions_annotations", []):
            annotation["supporting_locators"] = annotation.get("candidate_locators", [])
            annotation["review_status"] = STATUS
        for annotation in question.get("forbidden_claims_annotations", []):
            annotation["supporting_locators"] = annotation.get("candidate_locators", [])
            annotation["review_status"] = STATUS

        for group in question.get("accepted_chain_sets", []):
            for path in group["required_paths"]:
                for step in path["steps"]:
                    if step["relation_type"] != "PARENT_CHILD_CONTEXT":
                        key = (step["source"], step["target"])
                        step["relation_type"] = EDGE_TYPE_OVERRIDES.get(key, "DIRECT_REFERENCE")
                        step["review_status"] = STATUS
                    edge_counts[step["relation_type"]] = edge_counts.get(step["relation_type"], 0) + 1

        question["annotation_status"] = STATUS
        note = question.get("annotation_note", "").strip()
        audit_note = "AI-assisted audit against frozen Chapter III corpus; human sign-off still required."
        question["annotation_note"] = f"{note} {audit_note}".strip()

    metadata = payload["metadata"]
    metadata.update({
        "version": "0.3-ai-review-candidate",
        "status": STATUS,
        "review_provenance": {
            "reviewer": "OpenAI Codex",
            "reviewer_type": "AI_ASSISTED",
            "reviewed_on": "2026-10-31",
            "source_dataset_sha256": sha(V2),
            "locator_map_sha256": sha(MAP),
            "human_signoff": None,
        },
    })
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with SIGNOFF_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "question_id", "question", "category", "answerability", "gold_locators",
            "reference_answer", "human_decision", "reviewer", "review_date", "notes",
        ])
        writer.writeheader()
        for question in payload["questions"]:
            prior = prior_signoff.get(question["question_id"], {})
            revised = question["question_id"] in REVISED_QUESTION_IDS
            writer.writerow({
                "question_id": question["question_id"],
                "question": question["question"],
                "category": question["category"],
                "answerability": question["answerability"],
                "gold_locators": " | ".join(x["canonical_locator"] for x in question["gold_locations"]),
                "reference_answer": question["reference_answer"],
                "human_decision": "PENDING" if revised else prior.get("human_decision", "PENDING"),
                "reviewer": "" if revised else prior.get("reviewer", ""),
                "review_date": "" if revised else prior.get("review_date", ""),
                "notes": prior.get("notes", ""),
            })
    return {
        "output": str(OUTPUT),
        "human_signoff_csv": str(SIGNOFF_CSV),
        "questions": len(payload["questions"]),
        "unique_gold_locators": len(all_locators),
        "atomic_facts": sum(len(q.get("atomic_annotations", [])) for q in payload["questions"]),
        "exceptions": sum(len(q.get("required_exceptions_annotations", [])) for q in payload["questions"]),
        "forbidden_claims": sum(len(q.get("forbidden_claims_annotations", [])) for q in payload["questions"]),
        "role_counts": role_counts,
        "edge_counts": edge_counts,
        "category_corrections": CATEGORY_OVERRIDES,
        "content_corrections": ["B022", *sorted(ROUND1_REVISED_IDS)],
        "status": STATUS,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
