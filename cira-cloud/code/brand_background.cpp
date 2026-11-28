
// ciraGram: фирменный фон чата. Вместо однотонной заливки рисуется спокойный
// вертикальный переход тона и редкий узор из знаков ciraGram (облачко с буквой C).
// Узор рисуется один раз в плитку и дальше только копируется, поэтому почти бесплатен.
namespace {

constexpr auto kBrandTile = 176;
constexpr auto kBrandPi = 3.14159265358979323846;

void AddBrandGlyph(QPainterPath &path, QPointF center, double r, double angle) {
	const auto box = QRectF(-r, -r, 2. * r, 2. * r);
	auto arc = QPainterPath();
	arc.arcMoveTo(box, 42.);
	arc.arcTo(box, 42., 276.);
	auto ring = QPainterPathStroker();
	ring.setWidth(r * 0.46);
	ring.setCapStyle(Qt::RoundCap);
	ring.setJoinStyle(Qt::RoundJoin);
	auto glyph = ring.createStroke(arc);
	const auto at = [&](double degrees, double radius) {
		const auto a = degrees * kBrandPi / 180.;
		return QPointF(radius * std::cos(a), radius * std::sin(a));
	};
	auto tail = QPainterPath();
	tail.moveTo(at(103., r * 1.10));
	tail.lineTo(at(134., r * 1.58));
	tail.lineTo(at(160., r * 1.10));
	tail.closeSubpath();
	auto rounder = QPainterPathStroker();
	rounder.setWidth(r * 0.086);
	rounder.setJoinStyle(Qt::RoundJoin);
	glyph = glyph.united(tail.united(rounder.createStroke(tail)));
	auto transform = QTransform();
	transform.translate(center.x(), center.y());
	transform.rotate(angle);
	path.addPath(transform.map(glyph));
}

[[nodiscard]] QPixmap MakeBrandTile(const QColor &ink, int ratio) {
	auto image = QImage(
		QSize(kBrandTile, kBrandTile) * ratio,
		QImage::Format_ARGB32_Premultiplied);
	image.setDevicePixelRatio(ratio);
	image.fill(Qt::transparent);
	struct Mark {
		double x = 0.;
		double y = 0.;
		double angle = 0.;
	};
	constexpr Mark marks[] = {
		{ 38., 40., -14. },
		{ 126., 58., 10. },
		{ 76., 128., -6. },
		{ 150., 148., 16. },
	};
	auto path = QPainterPath();
	path.setFillRule(Qt::WindingFill);
	for (const auto &mark : marks) {
		AddBrandGlyph(path, QPointF(mark.x, mark.y), 8.5, mark.angle);
	}
	auto p = QPainter(&image);
	p.setRenderHint(QPainter::Antialiasing);
	p.setPen(Qt::NoPen);
	p.setBrush(ink);
	p.drawPath(path);
	constexpr QPointF dots[] = {
		{ 92., 22. }, { 20., 98. }, { 148., 104. }, { 112., 166. },
	};
	for (const auto &dot : dots) {
		p.drawEllipse(dot, 1.6, 1.6);
	}
	p.end();
	return QPixmap::fromImage(std::move(image));
}

[[nodiscard]] int PositiveModulo(int value, int by) {
	return ((value % by) + by) % by;
}

} // namespace

bool PaintBrandBackground(
		QPainter &p,
		QSize fill,
		QRect clip,
		const QColor &base) {
	if (fill.isEmpty() || clip.isEmpty() || !S::Bool(QString::fromUtf8(kBrandBackground))) {
		return false;
	}
	const auto lightness = base.lightnessF();
	const auto dark = (lightness < 0.5);
	auto top = QColor();
	auto bottom = QColor();
	auto ink = QColor();
	if (dark) {
		if (lightness < 0.06) {
			// Чистый чёрный встроенной ночной темы: чуть тёплый графит с лёгким сдвигом в синеву.
			top = QColor(0x17, 0x18, 0x1F);
			bottom = QColor(0x0E, 0x0F, 0x13);
		} else {
			top = base.lighter(112);
			bottom = base.darker(118);
		}
		ink = QColor(255, 255, 255, 11);
	} else {
		top = base.lighter(103);
		bottom = base.darker(105);
		ink = QColor(0x5B, 0x3F, 0xF0, 16);
	}
	struct Cache {
		QColor ink;
		int ratio = 0;
		QPixmap tile;
	};
	static auto cache = Cache();
	const auto ratio = style::DevicePixelRatio();
	if (cache.tile.isNull() || cache.ink != ink || cache.ratio != ratio) {
		cache.ink = ink;
		cache.ratio = ratio;
		cache.tile = MakeBrandTile(ink, ratio);
	}
	auto gradient = QLinearGradient(0., 0., 0., double(fill.height()));
	gradient.setColorAt(0., top);
	gradient.setColorAt(1., bottom);
	p.fillRect(clip, QBrush(gradient));
	p.drawTiledPixmap(
		clip,
		cache.tile,
		QPoint(
			PositiveModulo(clip.x(), kBrandTile),
			PositiveModulo(clip.y(), kBrandTile)));
	return true;
}
