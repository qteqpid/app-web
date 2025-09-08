import SwiftUI
import UIKit // 用于UIPasteboard功能

// Emoji图标展示视图，用于集中展示和查阅常用的精美emoji图标
struct IconView: View {
    // Emoji分类
    private let categories = [
        (name: "表情符号", icons: [
            "😊", "😂", "😍", "😘", "😢", "😠",
            "😴", "😎", "🤔", "😇", "😈", "👻",
            "🤩", "😋", "🤗", "😷", "🤫", "🤭"
        ]),
        (name: "手势符号", icons: [
            "👍", "👎", "👌", "✌️", "🤞", "🤟",
            "🤘", "👋", "🤚", "🖐️", "✋", "🖖",
            "🤙", "👈", "👉", "👆", "🖕", "👇"
        ]),
        (name: "自然元素", icons: [
            "☀️", "🌙", "⭐", "☁️", "🌈", "🌧️",
            "⛈️", "❄️", "⛄", "🔥", "💧", "🍃",
            "🌿", "🌾", "🌵", "🎄", "🌲", "🌳"
        ]),
        (name: "动物植物", icons: [
            "🐶", "🐱", "🐭", "🐹", "🐰", "🦊",
            "🐻", "🐼", "🐨", "🐯", "🦁", "🐮",
            "🐷", "🐸", "🐵", "🐔", "🐧", "🐦"
        ]),
        (name: "食物饮料", icons: [
            "🍎", "🍌", "🍊", "🍓", "🍇", "🍉",
            "🍒", "🍑", "🥭", "🍍", "🥥", "🥝",
            "🍅", "🥑", "🍆", "🥔", "🥕", "🌽"
        ]),
        (name: "交通工具", icons: [
            "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️",
            "🚓", "🚑", "🚒", "🚐", "🚚", "🚛",
            "🚜", "🚲", "🛵", "🏍️", "🚨", "🚔"
        ]),
        (name: "物品", icons: [
            "⌚", "📱", "💻", "🖥️", "🖨️", "🖱️",
            "🖲️", "🕹️", "🎮", "📷", "📸", "🎥",
            "🎤", "🎧", "📞", "☎️", "📠", "💽"
        ]),
        (name: "符号标志", icons: [
            "❤️", "🧡", "💛", "💚", "💙", "💜",
            "🖤", "🤍", "🤎", "💔", "❣️", "💕",
            "💞", "💓", "💗", "💖", "💘", "💝"
        ]),
        (name: "节日庆典", icons: [
            "🎂", "🎈", "🎉", "🎊", "🎁", "🎀",
            "🎏", "🎐", "🎪", "🎭", "🧨", "🎆",
            "🎇", "✨", "🎨", "🎫", "🎟️", "🎪"
        ]),
        (name: "其他常用", icons: [
            "🏠", "🏡", "🏢", "🏬", "🏪", "🏫",
            "🏥", "🏦", "🏨", "🏪", "🏩", "🏪",
            "💈", "🏬", "🏤", "🏣", "🏥", "🏦"
        ])
    ]

    var body: some View {
        NavigationStack {
            List(categories, id: \.name) { category in
                Section(header: Text(category.name).font(.headline).foregroundColor(.primary)) {
                    Grid(alignment: .center, horizontalSpacing: 16, verticalSpacing: 16) {
                        ForEach(0..<(category.icons.count + 3) / 4, id: \.self) { row in
                            GridRow {
                                ForEach(0..<4, id: \.self) {
                                    let index = row * 4 + $0
                                    if index < category.icons.count {
                                        IconCell(iconName: category.icons[index])
                                    }
                                }
                            }
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
            .navigationTitle("系统图标库")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// 单个图标单元格视图
struct IconCell: View {
    let iconName: String
    
    var body: some View {
        VStack {
            Text(iconName)
                .font(.system(size: 40))
            Text(getEmojiName(emoji: iconName))
                .font(.caption2)
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity)
        }
        .padding(8)
        .onTapGesture {
            // 复制图标名称到剪贴板
            UIPasteboard.general.string = iconName
        }
    }
}

// 预览提供器
struct IconView_Previews: PreviewProvider {
    static var previews: some View {
        IconView()
    }
}

// 获取Emoji的中文名称（简单映射）
func getEmojiName(emoji: String) -> String {
    let emojiNames: [String: String] = [
        "😊": "微笑", "😂": "大笑", "😍": "花痴", "😘": "飞吻",
        "😢": "哭泣", "😠": "生气", "😴": "睡觉", "😎": "酷",
        "🤔": "思考", "😇": "天使", "😈": "恶魔", "👻": "幽灵",
        "🤩": "崇拜", "😋": "馋", "🤗": "拥抱", "😷": "口罩",
        "👍": "赞", "👎": "踩", "👌": "OK", "✌️": "胜利",
        "☀️": "太阳", "🌙": "月亮", "⭐": "星星", "☁️": "云",
        "🌈": "彩虹", "🌧️": "下雨", "❄️": "雪花", "🔥": "火",
        "🐶": "狗", "🐱": "猫", "🐰": "兔子", "🐼": "熊猫",
        "🍎": "苹果", "🍌": "香蕉", "🍓": "草莓", "🍉": "西瓜",
        "🚗": "汽车", "🚕": "出租车", "🚌": "公交车", "✈️": "飞机",
        "⌚": "手表", "📱": "手机", "💻": "电脑", "📷": "相机",
        "❤️": "红心", "🧡": "橙心", "💛": "黄心", "💚": "绿心",
        "🎂": "蛋糕", "🎈": "气球", "🎉": "庆祝", "🎁": "礼物",
        "🏠": "房子", "🏢": "办公楼", "🏥": "医院", "🏫": "学校"
    ]
    
    return emojiNames[emoji] ?? ""
}
