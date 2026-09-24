import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it("renders operational state accessibly", () => {
    render(<RiskBadge level="CRITICAL" />);
    expect(screen.getByText("CRITICAL")).toBeInTheDocument();
  });
});
