import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: dialog
    title: "Thêm Thành Viên Mới"
    modal: true
    width: 400
    height: 300

    property alias name: nameInput.text
    property alias phone: phoneInput.text

    contentItem: ColumnLayout {
        spacing: 10
        TextField {
            id: nameInput
            placeholderText: "Tên thành viên"
            Layout.fillWidth: true
        }
        TextField {
            id: phoneInput
            placeholderText: "Số điện thoại"
            Layout.fillWidth: true
        }
    }

    footer: DialogButtonBox {
        Button {
            text: "Lưu"
            onClicked: {
                backend.addMember(nameInput.text, phoneInput.text)
                dialog.accept()
            }
        }
        Button {
            text: "Hủy"
            onClicked: dialog.reject()
        }
    }
}
