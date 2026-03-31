model_name = "ano"
use_jp_extra = True
batch_size = 4
epochs = 100
save_every_steps = 1000
normalize = False
trim = False
yomi_error = "skip"

if __name__ == "__main__":
    from gradio_tabs.train import preprocess_all
    from style_bert_vits2.nlp.japanese import pyopenjtalk_worker

    pyopenjtalk_worker.initialize_worker()

    preprocess_all(
        model_name=model_name,
        batch_size=batch_size,
        epochs=epochs,
        save_every_steps=save_every_steps,
        num_processes=2,
        normalize=normalize,
        trim=trim,
        freeze_EN_bert=False,
        freeze_JP_bert=False,
        freeze_ZH_bert=False,
        freeze_style=False,
        freeze_decoder=False,
        use_jp_extra=use_jp_extra,
        val_per_lang=0,
        log_interval=200,
        yomi_error=yomi_error,
    )