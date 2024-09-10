"use server";

import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { createStreamableValue } from "ai/rsc";
import { LiteralClient } from "@literalai/client";

const literalClient = new LiteralClient();
const streamTextMonitored =
  literalClient.instrumentation.vercel.instrument(streamText);

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export async function continueConversation(history: Message[]) {
  const stream = createStreamableValue();

  (async () => {
    const { textStream } = await streamTextMonitored({
      model: openai("gpt-3.5-turbo"),
      system: "You are a helpful assistant.",
      messages: history,
    });

    for await (const text of textStream) {
      stream.update(text);
    }

    stream.done();
  })();

  return {
    messages: history,
    newMessage: stream.value,
  };
}
