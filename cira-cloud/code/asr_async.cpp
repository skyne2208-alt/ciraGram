	// ciraGram: модель распознавания (38 МБ) грузится в фоне, а не в потоке интерфейса:
	// раньше окно подвисало при каждом запуске, а при первом ещё и на распаковке.
	crl::async([] {
		const auto ok = Engine::Instance().init();
		crl::on_main([ok] {
			if (!ok) {
				Settings::SetBool(kKeyEnabled, false);
			}
		});
	});
