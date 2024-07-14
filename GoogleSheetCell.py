class GoogleSheetCell:

    @staticmethod
    def formated_cell(text, color=(0, 0, 0), formula=False, bold=False, background=(1, 1, 1)):
        key = "formulaValue" if formula else "stringValue"
        return {
            "userEnteredFormat": {
                "textFormat": {
                    "foregroundColor": {
                        "red": color[0],
                        "green": color[1],
                        "blue": color[2]
                    },
                    'bold': bold and color != (0, 0, 0),
                },
                "backgroundColor": {
                    "red": background[0],
                    "green": background[1],
                    "blue": background[2]
                },
            },
            "userEnteredValue": {
                key: str(text)
            }
        }

