from typing import Any, Literal, NotRequired, TypedDict


class SourceRef(TypedDict):
    package_entry: str
    xml_path: str
    parent_asset_id: NotRequired[str | None]


class ParagraphRun(TypedDict):
    run_index: int
    text: str
    char_pr_id_ref: str | None
    child_tags: list[str]


class BlockAsset(TypedDict):
    schema_version: str
    asset_id: str
    asset_type: Literal["paragraph", "table", "image_occurrence", "masterpage"]
    source_ref: SourceRef
    section_id: NotRequired[str | None]
    page_no: NotRequired[int | None]
    page_source: NotRequired[str | None]
    text: NotRequired[str | None]
    embedded_object_refs: NotRequired[list[str]]
    extra: NotRequired[dict[str, Any]]


class ProofreadIssue(TypedDict):
    schema_version: str
    issue_id: str
    page: int | None
    origin_id: str
    source_location: str
    original_text: str
    suggested_fix: str
    reason: str
    memo: str
