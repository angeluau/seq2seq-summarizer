import torch
import torch.nn as nn
from torch import optim
from tqdm import tqdm
from utils import Dataset, show_plot
from model import Seq2Seq, DEVICE


def train_batch(batch, model, optimizer, criterion):
  _, input_tensor, target_tensor, input_lengths = batch

  optimizer.zero_grad()
  loss = model(input_tensor.to(DEVICE), target_tensor.to(DEVICE), input_lengths, criterion)
  loss.backward()
  optimizer.step()

  target_length = target_tensor.size(0)
  return loss.item() / target_length


def train(generator, vocab, model, n_batches=100, n_epochs=5, *, plot_every=20,
          learning_rate=0.01):
  plot_losses, cached_losses = [], []
  model.train()
  optimizer = optim.SGD(model.parameters(), lr=learning_rate)
  criterion = nn.NLLLoss(ignore_index=vocab.PAD)

  for epoch_count in range(1, n_epochs + 1):
    epoch_loss = 0
    prog_bar = tqdm(range(1, n_batches + 1), desc='Epoch %d' % epoch_count)

    for batch_count in prog_bar:
      batch = next(generator)
      loss = train_batch(batch, model, optimizer, criterion)

      epoch_loss += float(loss)
      epoch_avg_loss = epoch_loss / batch_count
      prog_bar.set_postfix(loss='%g' % epoch_avg_loss)

      cached_losses.append(loss)
      if batch_count % plot_every == 0:
        period_avg_loss = sum(cached_losses) / len(cached_losses)
        plot_losses.append(period_avg_loss)
        cached_losses = []

  show_plot(plot_losses)


if __name__ == "__main__":
  hidden_size = 100
  embed_size = 100
  batch_size = 4

  dataset = Dataset('data/org-sht.txt')
  vocabulary = dataset.build_vocab('eng')
  training_data = dataset.generator(batch_size, vocabulary, vocabulary)
  m = Seq2Seq(vocabulary, embed_size, hidden_size, dataset.src_len, dataset.tgt_len)

  train(training_data, vocabulary, m, n_batches=1000, n_epochs=5)
  torch.save(m.state_dict(), 'checkpoints/batsumm.pt')