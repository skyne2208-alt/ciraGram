	add({
		.key = QString::fromUtf8(kBrandBackground),
		.title = U(Ciragram::Lang::Tr("Фирменный фон ciraGram")),
		.description = U(Ciragram::Lang::Tr("Спокойный узор из знаков ciraGram вместо однотонного фона чата. Работает с однотонными обоями.")),
		.kind = S::Kind::Bool,
		.defaultValue = true,
	}, U(Ciragram::Lang::Tr("Обои")), "palette");
