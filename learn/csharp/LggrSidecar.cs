// C# client for learn/sidecar.py. AuthorityEffect: None.
// From the repository root: dotnet run --project learn/csharp
// Starts `python -m learn.sidecar`, sends one declaration and a few events,
// and prints each receipt status. Your harness calls Send() where its loop
// already hands off, steps, or reviews.
using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json.Nodes;

public sealed class LggrSidecar : IDisposable
{
    private readonly Process _process;

    public LggrSidecar(string repoRoot, string python = "python")
    {
        var info = new ProcessStartInfo(python, "-m learn.sidecar")
        {
            WorkingDirectory = repoRoot,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            UseShellExecute = false,
        };
        _process = Process.Start(info) ?? throw new InvalidOperationException("sidecar did not start");
    }

    // One line in, one receipt out.
    public JsonObject Send(JsonObject line)
    {
        _process.StandardInput.WriteLine(line.ToJsonString());
        _process.StandardInput.Flush();
        var reply = _process.StandardOutput.ReadLine() ?? throw new EndOfStreamException("sidecar closed");
        return JsonNode.Parse(reply)!.AsObject();
    }

    public void Dispose()
    {
        _process.StandardInput.Close();
        _process.WaitForExit();
        _process.Dispose();
    }

    public static int Main(string[] args)
    {
        var root = args.Length > 0 ? args[0] : Directory.GetCurrentDirectory();
        using var lggr = new LggrSidecar(root);

        Print(lggr.Send(new JsonObject
        {
            ["declare"] = new JsonObject
            {
                ["scope_id"] = "csharp-demo",
                ["query_scope"] = "every_prefix",
                ["bound"] = 1,
                ["global_sample_source"] = "external",
                ["authority_id"] = "release-owner",
                ["evaluator_id"] = "ci-local/v1",
                ["policy_id"] = "deploy-budget/v1",
            },
        }));

        // Two handoffs with the same message and different required tiers.
        Print(lggr.Send(Handoff("task-a", tier: 3)));
        var collision = lggr.Send(Handoff("task-b", tier: 1));
        Print(collision);

        // One step; the global sample comes from your own end-to-end check, not the agent.
        Print(lggr.Send(new JsonObject
        {
            ["event"] = "step",
            ["before"] = new JsonObject { ["state_id"] = "s0", ["value"] = 0 },
            ["after"] = new JsonObject { ["state_id"] = "s1", ["value"] = 1 },
            ["global_sample"] = 1,
        }));
        Print(lggr.Send(new JsonObject { ["event"] = "summary" }));

        return (string?)collision["status"] == "REPORT_INSUFFICIENT" ? 0 : 1;
    }

    private static JsonObject Handoff(string taskId, int tier) => new()
    {
        ["event"] = "handoff",
        ["state_id"] = taskId,
        ["report"] = new JsonObject { ["summary"] = "ship the etl job" },
        ["query"] = new JsonObject { ["approval_tier"] = tier },
    };

    private static void Print(JsonObject receipt) => Console.WriteLine((string?)receipt["status"]);
}
