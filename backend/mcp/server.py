from backend.mcp.tools import get_document_card, search_registry


def main() -> None:
    print("MCP tools dev check")

    search_result = search_registry(
        query="детская одежда",
        limit=5,
    )

    print("Search registry result:")
    print(search_result)

    if search_result["items"]:
        document_id = search_result["items"][0]["id"]

        card_result = get_document_card(document_id=document_id)

        print("Document card result:")
        print(card_result)


if __name__ == "__main__":
    main()