import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 1200
    height: 800
    title: backend.appName

    header: TabBar {
        id: tabBar
        currentIndex: 0
        TabButton { text: "Thành Viên" }
        TabButton { text: "Quản Lý Dây Hụi" }
        TabButton { text: "Tổng Quan" }
        TabButton { text: "Báo Cáo" }
    }

    Component {
        id: addMemberDialogComponent
        AddMemberDialog {}
    }

    StackLayout {
        id: stackLayout
        currentIndex: tabBar.currentIndex
        anchors.fill: parent

        // --- Members Tab ---
        ColumnLayout {
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                color: "#f8f8f8"
                border.color: "#e0e0e0"
                Button {
                    text: "Thêm Thành Viên"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    onClicked: {
                        var dialog = addMemberDialogComponent.createObject(window);
                        dialog.open();
                    }
                }
            }
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: backend.membersModel
                header: Rectangle {
                    width: parent.width; height: 40; color: "#f0f0f0"
                    GridLayout {
                        anchors.fill: parent; columns: 5
                        Label { text: "ID"; font.bold: true; Layout.fillWidth: true; padding: 5 }
                        Label { text: "Tên"; font.bold: true; Layout.fillWidth: true; padding: 5 }
                        Label { text: "SĐT"; font.bold: true; Layout.fillWidth: true; padding: 5 }
                        Label { text: "Địa chỉ"; font.bold: true; Layout.fillWidth: true; padding: 5 }
                        Label { text: "Trạng thái"; font.bold: true; Layout.fillWidth: true; padding: 5 }
                    }
                }
                delegate: Rectangle {
                    width: parent.width; height: 50
                    color: (index % 2 === 0) ? "#ffffff" : "#f9f9f9"
                    GridLayout {
                        anchors.fill: parent; columns: 5
                        Label { text: id; Layout.fillWidth: true; padding: 5 }
                        Label { text: name; Layout.fillWidth: true; padding: 5 }
                        Label { text: phone; Layout.fillWidth: true; padding: 5 }
                        Label { text: address; Layout.fillWidth: true; padding: 5 }
                        Label { text: status; Layout.fillWidth: true; padding: 5 }
                    }
                }
            }
        }

        // --- Hui List Tab ---
        Item {
            Label { text: "Quản Lý Dây Hụi - Sắp ra mắt"; anchors.centerIn: parent }
        }

        // --- Dashboard Tab ---
        Item {
            anchors.fill: parent
            GridLayout {
                anchors.fill: parent
                anchors.margins: 20
                columns: 2
                columnSpacing: 20
                rowSpacing: 20
                StatCard {
                    title: "Tổng Thành Viên"; value: backend.totalMembers; cardColor: "#3B82F6"
                }
                StatCard {
                    title: "Dây Hụi Đang Chạy"; value: backend.activeGroups; cardColor: "#10B981"
                }
                StatCard {
                    title: "Tổng Tiền Đã Đóng"; value: backend.totalIn; cardColor: "#EF4444"
                }
                StatCard {
                    title: "Tổng Tiền Đã Hốt"; value: backend.totalOut; cardColor: "#F59E0B"
                }
            }
        }

        // --- Reports Tab ---
        Item {
            Label { text: "Báo Cáo - Sắp ra mắt"; anchors.centerIn: parent }
        }
    }
}
