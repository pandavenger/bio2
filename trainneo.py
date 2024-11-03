from happytransformer import HappyGeneration, GENSettings, GENTrainArgs

happy_gen = HappyGeneration("GPT-NEO", "EleutherAI/gpt-neo-125M")
args = GENTrainArgs(learning_rate =1e-4, num_train_epochs = 3, batch_size= 1)
happy_gen.train("data/quotes_processed3.txt", args=args)
args = GENSettings(no_repeat_ngram_size=2, do_sample=True, early_stopping=False, top_k=50, temperature=0.7)
result = happy_gen.generate_text("Artificial intelligence will ")
print(result)
print(result.text)