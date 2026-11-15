declare module "d3-cloud" {
  export interface CloudWord {
    text: string;
    size: number;
    x: number;
    y: number;
    rotate: number;
    value?: number;
    full?: string;
    font?: string;
    weight?: string | number;
  }

  export interface CloudLayout {
    size(size: [number, number]): CloudLayout;
    words(words: Array<{ text: string; size: number; value?: number; full?: string }>): CloudLayout;
    padding(padding: number): CloudLayout;
    rotate(rotate: number | ((word: CloudWord, index: number) => number)): CloudLayout;
    font(font: string): CloudLayout;
    fontWeight(weight: string | number): CloudLayout;
    fontSize(size: number | ((word: CloudWord, index: number) => number)): CloudLayout;
    spiral(spiral: string): CloudLayout;
    on(event: "end", listener: (words: CloudWord[], bounds: Array<{ x: number; y: number }>) => void): CloudLayout;
    on(event: string, listener: (...args: unknown[]) => void): CloudLayout;
    start(): CloudLayout;
    stop(): CloudLayout;
  }

  export default function cloud(): CloudLayout;
}
