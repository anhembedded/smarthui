import QtQuick
import QtQuick.Controls

Rectangle {
    property string title: "Title"
    property string value: "Value"
    property color cardColor: "#3B82F6"

    width: 200
    height: 100
    color: "white"
    border.color: "#E2E8F0"
    radius: 12

    Column {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        padding: 15
        spacing: 5

        Label {
            text: title
            font.bold: true
            color: "#64748B"
        }
        Label {
            text: value
            font.pixelSize: 24
            font.bold: true
            color: "#1E293B"
        }
    }
}
