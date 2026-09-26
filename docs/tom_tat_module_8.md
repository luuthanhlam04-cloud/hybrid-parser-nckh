# Tóm tắt Module 8 — Hợp nhất đồ thị M4 và M7

## 1. Nhiệm vụ và ranh giới trách nhiệm

Nhiệm vụ cốt lõi của **Module 8 (M8)** là kết nối:

- **Physical Graph từ M4**: cấu trúc vật lý của văn bản pháp luật và vị trí
  nguồn của từng đoạn.
- **Canonical Semantic Graph từ M7**: các mention, concept, quy phạm, quan hệ
  và thông tin dẫn chiếu đã được M7 chuẩn hóa/phân loại.

M8 tạo **Unified Knowledge Graph (UKG)** để truy vấn được cả cấu trúc văn bản
lẫn ngữ nghĩa, đồng thời giữ đường dẫn truy vết về nguồn.

**M8 không phải module trích xuất hoặc phân loại ngữ nghĩa mới.** Cụ thể:

- Các node và quan hệ `ALLOW`, `REQUIRE`, `PROHIBIT`, `HAS_CONDITION`,
  `HAS_EXCEPTION`, `REFERENCE_TO` được M8 **tích hợp/chiếu** từ dữ liệu M7;
  M8 không tự trích xuất hoặc sáng tạo các quan hệ pháp lý này.
- Việc một tham chiếu là cùng Điều, cùng văn bản, ngoài phạm vi hay mơ hồ
  thuộc phân loại của **M7**. M8 giữ nguyên nhãn M7 nếu nhãn đó có trong input.
- Công việc của M8 đối với tham chiếu là tìm đích trong cây vật lý M4 theo
  hint/nội dung mà M7 cung cấp và tạo `RESOLVES_TO` nếu ghép được. Nếu không
  tìm thấy node tương ứng trong graph đầu vào, M8 ghi nhận trạng thái
  `TARGET_NOT_FOUND_IN_M4`; M8 không đổi nó thành một nhãn ngữ nghĩa mới.
- M8 không tự tạo node `DOCUMENT`. Nếu M4 không có node gốc văn bản để nối tới,
  tham chiếu cấp văn bản được báo là chưa tìm thấy đích trong M4. Muốn nối
  loại tham chiếu đó, hợp đồng M4 cần cung cấp node văn bản tương ứng.

Các kiểm tra SHACL, báo cáo xung đột tiềm tàng và cập nhật delta là các tiện
ích/quality gates chạy trên hoặc sau graph hợp nhất; chúng không thay đổi quyền
sở hữu phân loại ngữ nghĩa của M7.

---

## 2. Kiến trúc và công nghệ

### Thành phần chính

- **`src/fusion/fusion_engine.py`**: điều phối hợp nhất, bảo toàn node/cạnh M4,
  thêm dữ liệu ngữ nghĩa M7, gắn `MENTIONS`, phân giải tham chiếu về node vật
  lý và tạo báo cáo.
- **`src/fusion/m7_adapter.py`**: chuyển đổi hợp đồng M7 về dạng mà M8 có thể
  hợp nhất. Hỗ trợ schema `entities`/`relations` và schema mới hơn gồm
  `active_nodes`, `concepts`, `norms`, `active_edges` và `references`.
- **`src/fusion/node_mapper.py`**: tra cứu cây vật lý M4, dùng hint hoặc chuỗi
  dẫn chiếu của M7 để tìm node đích. Đây là thao tác **link dữ liệu**, không
  phải bộ phân loại scope.
- **`src/fusion/merge_policy.py`**: giữ phân biệt node `PHYSICAL` và
  `SEMANTIC`, tránh làm mất vai trò nguồn của M4/M7.
- **`src/fusion/graph_contract.py`**: kiểm tra ID, endpoint, kiểu quan hệ,
  evidence và các điều kiện hợp đồng trước khi hợp nhất.

### Công nghệ

| Công nghệ/kỹ thuật | Mục đích |
|---|---|
| Python | Fusion, mapping, kiểm tra đầu vào và tạo báo cáo |
| JSON | Hợp đồng trao đổi giữa M4, M7 và UKG |
| RDFLib | Biểu diễn graph dưới dạng RDF |
| pySHACL và SHACL/Turtle | Xác thực các constraint của graph hợp nhất |
| Quy tắc Python | Phát hiện cảnh báo xung đột quy phạm tiềm tàng |
| Isotonic regression (PAV) | Hiệu chuẩn confidence nếu có nhãn chuyên gia |
| Neo4j Python driver | Adapter hỗ trợ ghi graph delta vào Neo4j |
| pytest | Kiểm thử hợp nhất, dẫn chiếu, SHACL và delta |

SHACL chạy với `inference="none"`. Các thuộc tính kiểm tra cấu trúc được tính
trước theo các lượt tuyến tính rồi kiểm tra bằng SHACL property shapes, tránh
truy vấn SPARQL lặp trên toàn bộ các cạnh.
Các điều kiện cụ thể và giới hạn của chúng được tổng hợp trong bảng kiểm định
SHACL ở phần kết quả bên dưới.

### Công cụ và file chạy

- `run_fusion.py`: chạy M8 độc lập và xuất UKG, conflict report, SHACL report.
- `run_fusion_delta.py`: tính và áp dụng thay đổi graph lên Neo4j.
- `run_fusion_confidence_eval.py` và `run_fusion_quality_eval.py`: đánh giá
  trên CSV có nhãn.
- `scripts/sample_fusion_eval.py`: lấy mẫu quan hệ để chuyên gia gán nhãn;
  script không tự tạo gold labels.
- `run_pipeline.py`: điều phối các stage; M6 yêu cầu opt-in vì có thể phát
  sinh chi phí API.
- `tests/unit/test_fusion_engine.py`: test hợp nhất, contract, tham chiếu,
  SHACL, conflict, calibration và delta.

---

## 3. Luồng hợp nhất

1. Nạp Physical Graph M4 và Semantic Graph M7.
2. Dùng adapter để biểu diễn dữ liệu M7 theo hợp đồng nội bộ của M8; các giá
   trị semantic được chuyển tiếp từ M7, không được M8 phân loại lại.
3. Giữ lại cấu trúc và cạnh vật lý M4; đưa node và quan hệ M7 vào UKG.
4. Tạo cạnh `MENTIONS` để liên kết node văn bản nguồn của M4 với các entity/
   mention M7.
5. Với `REFERENCE_TO`, M8 dùng scope/hint M7 để quyết định có nên tìm đích
   trong graph M4 hay không. Khi tìm được node, tạo `RESOLVES_TO`; nếu không,
   vẫn giữ quan hệ semantic M7 và báo trạng thái liên kết.
6. Tạo báo cáo UKG; tùy chọn chạy các kiểm tra xung đột, SHACL hoặc delta.

Báo cáo tham chiếu phân biệt hai loại thông tin:

- `m7_scope`: scope do M7 cung cấp; có thể là `SAME_ARTICLE`,
  `SAME_DOCUMENT`, `EXTERNAL`, `AMBIGUOUS`, hoặc `null` nếu schema M7 đầu vào
  không có trường scope.
- `resolution_status`: kết quả nối sang M4 do M8 thực hiện:
  `RESOLVED_IN_M4`, `TARGET_NOT_FOUND_IN_M4`, `OUT_OF_SCOPE_PER_M7` hoặc
  `AMBIGUOUS_PER_M7`. Với scope không rỗng mà M8 không có quy tắc nối, trạng
  thái là `NOT_ATTEMPTED_PER_M7_SCOPE`; M8 giữ nguyên scope đó, không tự diễn
  giải nó thành loại khác.

Như vậy, `EXTERNAL`/`AMBIGUOUS` là nhãn nguồn M7; `TARGET_NOT_FOUND_IN_M4` là
kết quả tra cứu cấu trúc của M8. Chúng không phải các nhãn phân loại cạnh
tranh của cùng một tầng.

---

## 4. Đánh giá kết quả đầu ra thực tế

Dữ liệu chạy là graph Chương III Luật Đất đai 2024 đang có trong repository.
Các số liệu dưới đây được đọc từ UKG và báo cáo SHACL sau lần chạy M8:

### Quy mô đồ thị hợp nhất

| Nhóm đầu ra | Loại | Số lượng | Đánh giá |
|---|---|---:|---|
| Node | Vật lý từ M4 | 222 | Được giữ trong UKG |
| Node | Ngữ nghĩa từ M7 | 71 | Được tích hợp vào UKG |
| Node | Tổng UKG | 293 | Bằng tổng node M4 và M7 |
| Cạnh | Vật lý từ M4 | 551 | Gồm `BELONG_TO`, `NEXT`, `PREVIOUS` |
| Cạnh | Ngữ nghĩa từ M7 | 378 | Được giữ trong UKG |
| Cạnh | `MENTIONS` | 435 | Nối node vật lý với entity ngữ nghĩa |
| Cạnh | `RESOLVES_TO` | 5 | Nối target tham chiếu tìm được trong M4 |
| Quan hệ | Bị từ chối do lỗi hợp đồng/endpoint | 0 | Không có relation nào bị loại trong lần chạy |

### Phân bố quan hệ ngữ nghĩa M7 được tích hợp

| Loại quan hệ | Số lượng |
|---|---:|
| `ALLOW` | 157 |
| `REQUIRE` | 39 |
| `PROHIBIT` | 8 |
| `HAS_CONDITION` | 22 |
| `HAS_OBJECT` | 125 |
| `REFERENCE_TO` | 27 |
| **Tổng quan hệ ngữ nghĩa** | **378** |

### Kết quả kiểm tra và đánh giá chất lượng

| Tiêu chí | Kết quả | Nhận xét |
|---|---:|---|
| Unit tests M8 | 20/20 PASS | Bao phủ hợp nhất, tham chiếu, SHACL, conflict, calibration và delta |
| SHACL | `conforms: true` | UKG đạt các constraint SHACL được cấu hình |
| Relation bị từ chối | 0 | Không phát hiện relation lỗi endpoint/hợp đồng trong lần chạy |
| Cảnh báo xung đột quy phạm | 1 | Cảnh báo heuristic `REQUIRE_PROHIBIT`, cần chuyên gia xem xét |
| Confidence | `heuristic_uncalibrated` | Chưa thể diễn giải là xác suất đã hiệu chuẩn |

### Chi tiết kiểm định SHACL

| Nhóm kiểm tra | Điều kiện được kiểm tra | Kết quả lần chạy | Giới hạn cần lưu ý |
|---|---|---|---|
| Endpoint cạnh | Mỗi cạnh có loại cạnh và source/target tồn tại trong UKG | Đạt; `conforms: true` | Không đánh giá cạnh có đúng về mặt pháp lý hay không |
| Số Điều | Node `ARTICLE` phải có số nguyên dương | Đạt; `conforms: true` | Không kiểm tra số Điều có đầy đủ/liên tục so với toàn văn luật |
| Quan hệ cấu trúc | `BELONG_TO` tuân theo cặp cấp cha-con được cấu hình; cây không có chu trình | Đạt; `conforms: true` | Chỉ áp dụng cho các cấp cấu trúc đã khai báo |
| Quan hệ thứ tự | `NEXT`/`PREVIOUS` phải nối node cùng cấp cấu trúc | Đạt; `conforms: true` | Chưa xác nhận thứ tự số/vị trí tăng dần hoặc tính đối ứng giữa `NEXT` và `PREVIOUS` |
| Domain/range ngữ nghĩa | Khi cả hai đầu mút có ontology class, cặp lớp phải thuộc miền/đích được cấu hình cho loại quan hệ | Đạt; `conforms: true` | Nếu thiếu ontology class ở một đầu mút, kiểm tra hiện tại chưa đánh dấu vi phạm; kết quả không thay thế thẩm định ngữ nghĩa bởi chuyên gia |

Các điều kiện trên được tính thành thuộc tính kiểm tra rồi SHACL xác thực.
Runner `run_pipeline.py` và `run_fusion.py` ghi báo cáo SHACL; nếu
`conforms: false`, runner phát sinh lỗi và không ghi UKG mới như một lần chạy
thành công. Kết quả `conforms: true` xác nhận graph đạt các constraint hiện
được cấu hình, không đồng nghĩa toàn bộ nội dung pháp lý đã chính xác.

### Kết quả liên kết tham chiếu

| Trạng thái liên kết | Số quan hệ | Tỷ lệ trên 27 tham chiếu |
|---|---:|---:|
| `RESOLVED_IN_M4` | 6 | 22,2% |
| `TARGET_NOT_FOUND_IN_M4` | 21 | 77,8% |
| **Tổng `REFERENCE_TO`** | **27** | **100%** |

Trong graph M7 legacy hiện dùng cho lần chạy này, các relation không mang
`reference_scope` hoặc `target_hint`; bởi vậy report ghi `m7_scope: null`.
Tỷ lệ trên chỉ mô tả khả năng liên kết vào lát cắt M4 hiện có, không phải độ
chính xác phân loại tham chiếu. Sáu là số relation được ghép về M4; một
relation có thể chứa nhiều target và tạo nhiều cạnh. Vì vậy số relation đã
resolve và số cạnh `RESOLVES_TO` không nhất thiết bằng nhau.

`TARGET_NOT_FOUND_IN_M4` chỉ có nghĩa là chưa tìm được node đích trong graph
đầu vào; không thể kết luận tham chiếu là ngoài phạm vi hay M7 phân loại sai.

Cảnh báo xung đột hiện có là `REQUIRE_PROHIBIT`, IDs
`REL_REL_0765` và `REL_REL_0777`. Đây là cảnh báo heuristic để người có chuyên
môn xem xét điều kiện/ngoại lệ, không phải phán quyết về mâu thuẫn pháp luật.
Các số liệu trên đánh giá cấu trúc và kết quả chạy; độ chính xác pháp lý cần
được đo riêng bằng gold dataset đã được chuyên gia gán nhãn.

---

## 5. Cách chạy

```powershell
python run_fusion.py
python -m pytest tests/unit/test_fusion_engine.py -q
```

Sinh mẫu CSV đánh giá:

```powershell
python scripts/sample_fusion_eval.py --size 80 --seed 42
```

Confidence hiện là heuristic chưa hiệu chuẩn cho đến khi có nhãn chuyên gia
đủ tin cậy. Không xem các template chưa được gán nhãn là gold dataset.

---

## 6. Giới hạn và hướng hoàn thiện

- M8 chỉ phân giải được tham chiếu về những node thực sự có trong M4. Nếu graph
  đầu vào chỉ là một chương, dẫn chiếu tới Điều ở chương khác sẽ có trạng thái
  `TARGET_NOT_FOUND_IN_M4`; cần nạp phạm vi văn bản rộng hơn nếu muốn nối đích.
- Schema M7 legacy không có scope/hint thì M8 báo `m7_scope: null`; muốn phân
  biệt rõ tham chiếu nội bộ, ngoài phạm vi và mơ hồ thì cần M7 xuất các nhãn
  đó theo contract.
- Muốn resolve “Luật này” về toàn văn, M4 cần cung cấp node `DOCUMENT` cùng ID
  ổn định và quy tắc nối rõ ràng. M8 không tự bịa node văn bản.
- Confidence chưa được kiểm định/hiệu chuẩn bằng gold labels chuyên gia.
- Conflict detection mới tạo cảnh báo theo luật; chưa thay thế phân tích pháp
  lý toàn diện.
- Adapter Neo4j có kiểm thử đơn vị nhưng chưa được xác nhận trên server Neo4j
  mục tiêu.

## 7. Kết luận

M8 thực hiện vai trò **tích hợp và liên kết M4–M7**: giữ cấu trúc M4, đưa dữ
liệu ngữ nghĩa M7 vào UKG, neo dữ liệu về vị trí nguồn và tìm đích dẫn chiếu
trong graph vật lý. M7 vẫn là nguồn chịu trách nhiệm phân loại ngữ nghĩa và
scope dẫn chiếu. Trên bộ dữ liệu hiện tại, kiểm thử M8 và SHACL pass; đánh giá
độ chính xác pháp lý vẫn cần gold set do chuyên gia gán nhãn.
